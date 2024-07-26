import os, glob
import tifffile
import numpy as np
import matplotlib.pyplot as plt
from time import time
from scipy.ndimage import shift, gaussian_filter
from skimage.registration import phase_cross_correlation

from joblib import Parallel, delayed
from multiprocessing import cpu_count

CPU_COUNT = cpu_count()

def make_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)
    
def make_filelist(path, crop_start=0, crop_end=None):
    return sorted(glob.glob(os.path.join(path, '*.tif')))[crop_start:crop_end]

def get_bounds(filelist, padding):
    frame_shape = tifffile.imread(filelist[0]).shape

    is_mask_zero = True
    test_frame = tifffile.imread(filelist[0])
    mask = (test_frame>0).astype('int')
    if np.max(mask) - np.min(mask) == 0:
        is_mask_zero = False

    def loop(file):
        frame = tifffile.imread(file)
        if is_mask_zero == True:
            indices = np.where(frame>0)
        else:
            indices = np.where(frame<255)
        return [indices[0].min(), indices[0].max(), indices[1].min(), indices[1].max()]

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    def loop(file):
        frame = tifffile.imread(file)
        indices = np.where(frame>0)
        return [indices[0].min(), indices[0].max(), indices[1].min(), indices[1].max()]

    n_jobs = np.minimum(cpu_count(),len(filelist))
    results = Parallel(n_jobs=n_jobs)(delayed(loop)(file) for file in filelist)
    results = np.asarray(results)
    
    bounds = [min(results[:,0]), max(results[:,1]), min(results[:,2]), max(results[:,3])]
    bounds = [max(bounds[0]-padding, 0), min(bounds[1]+padding, frame_shape[0]), max(bounds[2]-padding, 0), min(bounds[3]+padding, frame_shape[1])]
    return bounds

def get_means(filelist, means_smoothing):

    def loop(file):
        frame = tifffile.imread(file).astype("float")
        mean = np.sum(frame)/np.sum(frame>0)
        return mean

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    means = Parallel(n_jobs=n_jobs)(delayed(loop)(file) for file in filelist)
    means = np.asarray(means)
    means = gaussian_filter(means, means_smoothing)
    return means

def crop_data(filelist, save_path, padding):

    bounds = get_bounds(filelist, padding)

    make_dir(save_path)

    def loop(file):
        frame = tifffile.imread(file)[bounds[0]:bounds[1],bounds[2]:bounds[3]]
        filename = os.path.split(file)[1]
        tifffile.imwrite(os.path.join(save_path, filename), frame)

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    _ = Parallel(n_jobs=n_jobs)(delayed(loop)(file) for file in filelist)

def normalize_data(filelist, save_path, means_smoothing):
    make_dir(save_path)

    means = get_means(filelist, means_smoothing)
    total_mean = means.mean()

    def loop(file, curr_mean):
        frame = tifffile.imread(file).astype("float")
        zero_mask = frame <= 0
        frame = frame - curr_mean + total_mean
        frame[zero_mask]=0
        frame = frame.astype("uint8")
        filename = os.path.split(file)[1]
        tifffile.imwrite(os.path.join(save_path, filename), frame)

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    _ = Parallel(n_jobs=n_jobs)(delayed(loop)(file, curr_mean) for file, curr_mean in zip(filelist, means))

def invert_data(filelist, save_path):
    make_dir(save_path)

    def loop(file):
        frame = tifffile.imread(file)
        frame = 255-frame
        filename = os.path.split(file)[1]
        tifffile.imwrite(os.path.join(save_path, filename), frame)

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    _ = Parallel(n_jobs=n_jobs)(delayed(loop)(file) for file in filelist)

def get_range(array):
    array = array.astype('float')
    return np.max(array)-np.min(array)

def get_inner_rectangle(mask, step):
    up, down, left, right = False, False, False, False

    while min([up,down,left,right])==0:
        indices = np.where(mask==1)
        y_min, y_max, x_min, x_max = indices[0].min(), indices[0].max(), indices[1].min(), indices[1].max()

        new_mask = mask.copy()

        line_up = mask[y_min,x_min:x_max]
        if get_range(line_up)==0:
            up = True
        else:
            new_mask[:y_min+step,:]=0

        line_down = mask[y_max,x_min:x_max]
        if get_range(line_down)==0:
            down = True
        else:
            new_mask[y_max-step:,:]=0

        line_left = mask[y_min:y_max,x_min]
        if get_range(line_left)==0:
            left = True
        else:
            new_mask[:,:x_min+step]=0

        line_right = mask[y_min:y_max,x_max]
        if get_range(line_right)==0:
            right = True
        else:
            new_mask[:,x_max-step:]=0
            
        mask = new_mask.copy()

    indices = np.where(mask==1)
    y_min, y_max, x_min, x_max = indices[0].min(), indices[0].max(), indices[1].min(), indices[1].max()
        
    return y_min, y_max, x_min, x_max

def get_PCC(reference_frame, moving_frame, bounds, upsample_factor):
    y_min, y_max, x_min, x_max = bounds
    translation = phase_cross_correlation(reference_frame[y_min:y_max,x_min:x_max], moving_frame[y_min:y_max,x_min:x_max], upsample_factor=upsample_factor, normalization=None)[0]
    return translation

def get_translation(filelist, upsample_factor, mask_crop_step):

    dx = []
    dx.append([0,0])

    def loop(z):
        reference_frame, moving_frame = tifffile.imread(filelist[z-1]).astype('float'), tifffile.imread(filelist[z]).astype('float')
        reference_mask, moving_mask = reference_frame<255, moving_frame<255
        mask = reference_mask*moving_mask
        y_min, y_max, x_min, x_max = get_inner_rectangle(mask, mask_crop_step)
        
        translation = get_PCC(reference_frame, moving_frame, [y_min, y_max, x_min, x_max], upsample_factor)

        return translation

    n_jobs = np.minimum(CPU_COUNT,len(filelist)-1)
    results = Parallel(n_jobs=n_jobs)(delayed(loop)(z) for z in range(1,len(filelist)))
    
    dx.extend(results)
    dx = np.cumsum(np.asarray(dx),axis=0)

    return dx

def pad_from_translation(translation):
    dx_before = np.clip(-translation, 0, None)
    dx_after = np.clip(translation, 0, None)

    before_0 = int(np.max(dx_before[:,0]))
    before_1 = int(np.max(dx_before[:,1]))
    after_0 = int(np.max(dx_after[:,0]))
    after_1 = int(np.max(dx_after[:,1]))

    return ((before_0, after_0),(before_1, after_1))

def register_frames(filelist, translation, save_path):

    pad = pad_from_translation(translation)

    def loop(file, dx):
        frame = tifffile.imread(file).astype('float')
        frame = np.pad(frame, pad, mode='edge')
        
        mask = (frame<255)
        mask = shift(mask, np.round(dx), cval=0, order=0)
        
        frame = shift(frame, dx, cval=255)
        frame = frame.astype("uint8")
        frame = frame*mask + 255*(~mask)
        frame = frame.astype("uint8")
        
        filename = os.path.split(file)[1]
        tifffile.imwrite(os.path.join(save_path, filename), frame)

    n_jobs = np.minimum(CPU_COUNT,len(filelist))
    _ = Parallel(n_jobs=n_jobs)(delayed(loop)(file, dx) for file, dx in zip(filelist, translation))

def registration(load_path, save_path, upsample_factor, mask_crop_step):

    make_dir(save_path)

    filelist = make_filelist(load_path)

    translation = get_translation(filelist, upsample_factor, mask_crop_step)

    register_frames(filelist, translation, save_path)




