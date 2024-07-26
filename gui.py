import os
import sys
import tkinter as tk
from tkinter import ttk, filedialog

from utils import *

INITIAL_DIR = "/nfs/data1expansion/FIBSEM_datasync3"
FRAME_PAD = 5
FRAME_RELIEF = tk.RAISED
FRAME_BORDERWIDTH = 1
WIDGET_PAD = 3

PAD_DEFAULT = 50
SMOOTH_DEFAULT = 5
UPSAMPLE_DEFAULT = 100
MASKCROP_DEFAULT = 50

class ToolTip(object):
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tip_window = None
        widget.bind("<Enter>", self.show_tip)
        widget.bind("<Leave>", self.hide_tip)

    def show_tip(self, event=None):
        if self.tip_window or not self.text:
            return
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1)
        label.pack(ipadx=1)

    def hide_tip(self, event=None):
        tw = self.tip_window
        self.tip_window = None
        if tw:
            tw.destroy()

class MainFrame(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("FIBSEM Registration")
        
        frame_root = tk.Frame(self, padx=FRAME_PAD, pady=FRAME_PAD)
        frame_root.pack()

        ############################################ CHOOSE TASKS

        frame_task = tk.Frame(frame_root, borderwidth = FRAME_BORDERWIDTH, relief=FRAME_RELIEF, padx=FRAME_PAD, pady=FRAME_PAD)
        frame_task.grid(column=0, row=0, padx=FRAME_PAD, pady=FRAME_PAD)

        self.var_task_crop = tk.IntVar()
        self.var_task_norm = tk.IntVar()
        self.var_task_invert = tk.IntVar()

        frame_preprocessing = tk.Frame(frame_task)

        def make_frame_preprocessing():
            frame_preprocessing.grid(column=0, row=1, columnspan=3, padx=WIDGET_PAD, pady=WIDGET_PAD)
            
            label_preprocessing = tk.Label(frame_preprocessing, text ="Preprocessing subtasks:")
            label_preprocessing.grid(column=0, row=0, columnspan=3)
            checkbutton_crop = tk.Checkbutton(frame_preprocessing, text='Crop',variable=self.var_task_crop, onvalue=1, offvalue=0)
            checkbutton_crop.grid(column=0, row=1)
            checkbutton_norm = tk.Checkbutton(frame_preprocessing, text='Normalize',variable=self.var_task_norm, onvalue=1, offvalue=0)
            checkbutton_norm.grid(column=1, row=1)
            checkbutton_invert = tk.Checkbutton(frame_preprocessing, text='Invert',variable=self.var_task_invert, onvalue=1, offvalue=0)
            checkbutton_invert.grid(column=2, row=1)

        def forget_frame_preprocessing():
            frame_preprocessing.grid_forget()
        
        self.var_task = tk.StringVar()
        self.var_task.set("registration")
        label_task = tk.Label(frame_task, text ="Task:")
        button_preprocessing = ttk.Radiobutton(frame_task, text='Preprocessing', variable=self.var_task, value='preprocessing', command=make_frame_preprocessing)
        button_registration = ttk.Radiobutton(frame_task, text='Registration', variable=self.var_task, value='registration', command=forget_frame_preprocessing)

        label_task.grid(column=0, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        button_preprocessing.grid(column=1, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        button_registration.grid(column=2, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)

        ############################################ SET NUMBER OF EXPERIMENTS

        frame_numexp = tk.Frame(frame_root, borderwidth = FRAME_BORDERWIDTH, relief=FRAME_RELIEF, padx=FRAME_PAD, pady=FRAME_PAD)
        frame_numexp.grid(column=0, row=1, padx=FRAME_PAD, pady=FRAME_PAD)

        self.init_numexp = False
        self.var_numexp = tk.IntVar()
        self.var_numexp.set(1)

        def select_load_path(i):
            filepath = filedialog.askdirectory( initialdir=INITIAL_DIR )
            self.var_load_paths[i].set(filepath)
            self.lift()

        def select_save_path(i):
            filepath = filedialog.askdirectory( initialdir=INITIAL_DIR )
            self.var_save_paths[i].set(filepath)
            self.lift()

        def make_frame_dir(numexp):
            self.frame_dir = tk.Frame(frame_numexp)

            self.label_dir = [tk.Label(self.frame_dir, text="Exp #"+str(i+1)+":") for i in range(numexp)]
            self.entry_load = [tk.Entry(self.frame_dir, textvariable=self.var_load_paths[i]) for i in range(numexp)]
            self.button_load = [tk.Button(self.frame_dir, text="Load dir", command=lambda x=i : select_load_path(x)) for i in range(numexp)]
            self.entry_save = [tk.Entry(self.frame_dir, textvariable=self.var_save_paths[i]) for i in range(numexp)]
            self.button_save = [tk.Button(self.frame_dir, text="Save dir", command=lambda x=i : select_save_path(x)) for i in range(numexp)]
            self.label_crop_start = [tk.Label(self.frame_dir, text="Crop start:") for i in range(numexp)]
            self.entry_crop_start = [tk.Entry(self.frame_dir, textvariable=self.var_crop_start[i], width=5) for i in range(numexp)]
            self.label_crop_end = [tk.Label(self.frame_dir, text="Crop end:") for i in range(numexp)]
            self.entry_crop_end = [tk.Entry(self.frame_dir, textvariable=self.var_crop_end[i], width=5) for i in range(numexp)]

            for i in range(numexp):
                self.label_dir[i].grid(column=0, row=i)
                self.entry_load[i].grid(column=1, row=i)
                self.button_load[i].grid(column=2, row=i)
                self.entry_save[i].grid(column=3, row=i)
                self.button_save[i].grid(column=4, row=i)
                self.label_crop_start[i].grid(column=5, row=i)
                self.entry_crop_start[i].grid(column=6, row=i)
                self.label_crop_end[i].grid(column=7, row=i)
                self.entry_crop_end[i].grid(column=8, row=i)

            self.frame_dir.grid(column=0, row=1, padx=WIDGET_PAD, pady=WIDGET_PAD)
        
        def update_numexp():
            if self.init_numexp==True:
                self.frame_dir.grid_forget()
            self.init_numexp=True
            
            numexp = self.var_numexp.get()
            self.var_load_paths = [tk.StringVar() for _ in range(numexp)]
            self.var_save_paths = [tk.StringVar() for _ in range(numexp)]
            self.var_crop_start = [tk.StringVar() for _ in range(numexp)]
            self.var_crop_end = [tk.StringVar() for _ in range(numexp)]
            for i in range(numexp):
                self.var_load_paths[i].set("")
                self.var_save_paths[i].set("")
                self.var_crop_start[i].set("0")
                self.var_crop_end[i].set("")

            make_frame_dir(numexp)

        frame_numexp_set = tk.Frame(frame_numexp)
        frame_numexp_set.grid(column=0, row=0)

        label_numexp = tk.Label(frame_numexp_set, text ="# of experiments:")
        spinbox_numexp = tk.Spinbox(frame_numexp_set, from_=1, to=10, textvariable=self.var_numexp, width=2)
        button_numexp = tk.Button(frame_numexp_set, text="Set", command=update_numexp)
        ttip_numexp = tk.Label(frame_numexp_set, text ="?", relief="raised")
        ToolTip(ttip_numexp, "Dirs: double-click the dir you want to select. \nSave dir: if it doesn't exist yet, type it manually in the entry box. \nCrop end: set as empty if you want to go to the end of the stack.")

        label_numexp.grid(column=0, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        spinbox_numexp.grid(column=1, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        button_numexp.grid(column=2, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        ttip_numexp.grid(column=3, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)

        ############################################ OPTIONAL PARAMETERS

        frame_optional = tk.Frame(frame_root, borderwidth = FRAME_BORDERWIDTH, relief=FRAME_RELIEF, padx=FRAME_PAD, pady=FRAME_PAD)
        frame_optional.grid(column=0, row=2, padx=FRAME_PAD, pady=FRAME_PAD)

        def toggle_optional():
            if button_toggle.config('relief')[-1]=='sunken':
                frame_optional_set.grid_forget()
                button_toggle.config(text="Show optional parameters", relief='raised')
            else:
                frame_optional_set.grid(column=0, row=1, padx=WIDGET_PAD, pady=WIDGET_PAD)
                button_toggle.config(text="Hide optional parameters", relief='sunken')

        button_toggle = tk.Button(frame_optional, text="Show optional parameters", command=toggle_optional, relief="raised")
        button_toggle.grid(column=0, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)

        self.var_pad = tk.IntVar()
        self.var_pad.set(PAD_DEFAULT)
        self.var_smooth = tk.IntVar()
        self.var_smooth.set(SMOOTH_DEFAULT)
        self.var_upsample = tk.IntVar()
        self.var_upsample.set(UPSAMPLE_DEFAULT)
        self.var_maskcrop = tk.IntVar()
        self.var_maskcrop.set(MASKCROP_DEFAULT)

        frame_optional_set = tk.Frame(frame_optional)
        
        label_pad = tk.Label(frame_optional_set, text="Crop padding:")
        spinbox_pad = tk.Spinbox(frame_optional_set, from_=0, to=200, textvariable=self.var_pad, width=3)
        ttip_pad = tk.Label(frame_optional_set, text ="?", relief="raised")      
        ToolTip(ttip_pad, "Padding (in pixels) added around the data after it is cropped. \nPart of Preprocessing.")
        label_pad.grid(column=0, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        spinbox_pad.grid(column=1, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)
        ttip_pad.grid(column=2, row=0, padx=WIDGET_PAD, pady=WIDGET_PAD)

        label_smooth = tk.Label(frame_optional_set, text="Means curve smoothing:")
        spinbox_smooth = tk.Spinbox(frame_optional_set, from_=1, to=10, textvariable=self.var_smooth, width=2)
        ttip_smooth = tk.Label(frame_optional_set, text ="?", relief="raised")      
        ToolTip(ttip_smooth, "Strength of the smoothing of the per-frame means curve, which is used for the intensity normalization along Z. \nIncrease it to ignore per-frame fluctuations, at the risk of oversmoothing the actual intensity trend. \nPart of Preprocessing.")
        label_smooth.grid(column=0, row=1, padx=WIDGET_PAD, pady=WIDGET_PAD)
        spinbox_smooth.grid(column=1, row=1, padx=WIDGET_PAD, pady=WIDGET_PAD)
        ttip_smooth.grid(column=2, row=1, padx=WIDGET_PAD, pady=WIDGET_PAD)

        label_upsample= tk.Label(frame_optional_set, text="Upsample factor:")
        spinbox_upsample = tk.Spinbox(frame_optional_set, from_=1, to=100, textvariable=self.var_upsample, width=3)
        ttip_upsample = tk.Label(frame_optional_set, text ="?", relief="raised")      
        ToolTip(ttip_upsample, "The registration algorithm returns translation values up to 1/(upsample factor) precision. \nIf equal to 1, for example, it will only return integer values. \nPart of Registration.")
        label_upsample.grid(column=0, row=2, padx=WIDGET_PAD, pady=WIDGET_PAD)
        spinbox_upsample.grid(column=1, row=2, padx=WIDGET_PAD, pady=WIDGET_PAD)
        ttip_upsample.grid(column=2, row=2, padx=WIDGET_PAD, pady=WIDGET_PAD)

        label_maskcrop= tk.Label(frame_optional_set, text="Mask crop step:")
        spinbox_maskcrop = tk.Spinbox(frame_optional_set, from_=1, to=100, textvariable=self.var_maskcrop, width=3)
        ttip_maskcrop = tk.Label(frame_optional_set, text ="?", relief="raised")      
        ToolTip(ttip_maskcrop, "Step (in pixels) used in the algorithm for finding the largest rectangle inside the cell. \nIncrease it for performance, decrease it for accuracy. \nPart of Registration.")
        label_maskcrop.grid(column=0, row=3, padx=WIDGET_PAD, pady=WIDGET_PAD)
        spinbox_maskcrop.grid(column=1, row=3, padx=WIDGET_PAD, pady=WIDGET_PAD)
        ttip_maskcrop.grid(column=2, row=3, padx=WIDGET_PAD, pady=WIDGET_PAD)

        def reset_optional():
            self.var_pad.set(PAD_DEFAULT)
            self.var_smooth.set(SMOOTH_DEFAULT)
            self.var_upsample.set(UPSAMPLE_DEFAULT)
            self.var_maskcrop.set(MASKCROP_DEFAULT)

        button_reset = tk.Button(frame_optional_set, text="Reset to default", command=reset_optional)
        button_reset.grid(column=0, row=4, padx=WIDGET_PAD, pady=WIDGET_PAD, columnspan=3)
 

        ############################################ RUN

        def check_parameters():
            self.params = {}
            
            self.params["task"] = self.var_task.get()
            if self.params["task"]=="preprocessing":
                self.params["crop"] = self.var_task_crop.get()
                self.params["norm"] = self.var_task_norm.get()
                self.params["invert"] = self.var_task_invert.get()
                if self.params["crop"]+self.params["norm"]+self.params["invert"]==0:
                    tk.messagebox.showwarning(title="Error", message="Select at least one subtask")
                    return False
                    
            self.params["numexp"] = self.var_numexp.get()
            if not hasattr(self, 'var_load_paths'):
                tk.messagebox.showwarning(title="Error", message="Please set the number of experiments")
                return False
            self.params["load_paths"] = [self.var_load_paths[i].get() for i in range(self.params["numexp"])]
            self.params["save_paths"] = [self.var_save_paths[i].get() for i in range(self.params["numexp"])]
            self.params["crop_start"] = [self.var_crop_start[i].get() for i in range(self.params["numexp"])]
            self.params["crop_end"] = [self.var_crop_end[i].get() for i in range(self.params["numexp"])]

            for i in range(self.params["numexp"]):
                if not os.path.isdir(self.params["load_paths"][i]):
                    tk.messagebox.showwarning(title="Error", message="Load dir #"+str(i+1)+" does not exist")
                    return False
                if self.params["save_paths"][i]=="":
                    tk.messagebox.showwarning(title="Error", message="Please specify save dir #"+str(i+1))
                    return False
                if self.params["crop_end"][i]!="":
                    if int(self.params["crop_end"][i])<=int(self.params["crop_start"][i]):
                        tk.messagebox.showwarning(title="Error", message="Crop start #"+str(i+1)+" should be smaller than its corresponding crop end")
                        return False

            self.params["pad"] = self.var_pad.get()
            self.params["smooth"] = self.var_smooth.get()
            self.params["upsample"] = self.var_upsample.get()
            self.params["maskcrop"] = self.var_maskcrop.get()

            return True

        def run_code():
            if check_parameters()==True:
                self.destroy()

        button_run = tk.Button(frame_root, text="Run", command=run_code)
        button_run.grid(column=0, row=3)

        self.protocol("WM_DELETE_WINDOW", self.on_closing) 

    def on_closing(self):
        self.destroy()
        sys.exit()
        
app=MainFrame()
app.mainloop()

######################### RUN CODE

params = app.params

start = time()

for i in range(params["numexp"]):
    params["crop_start"][i] = int(params["crop_start"][i])
    if params["crop_end"][i]=="":
        params["crop_end"][i] = None
    else:
        params["crop_end"][i] = int(params["crop_end"][i])

if params["task"]=="preprocessing":
    print("Processing data...")

    for i in range(params['numexp']):
        start_time = time()

        load_path, save_path = params["load_paths"][i], params["save_paths"][i]
        crop_start, crop_end = params["crop_start"][i], params["crop_end"][i]
        padding = params["pad"]
        means_smoothing = params["smooth"]

        filelist = make_filelist(load_path, crop_start, crop_end)

        if params['crop']==1:
            crop_data(filelist, save_path, padding)
            filelist = make_filelist(save_path)

        if params['norm']==1:
            normalize_data(filelist, save_path, means_smoothing)
            filelist = make_filelist(save_path)

        if params['invert']==1:
            invert_data(filelist, save_path)

        total_time = time()-start_time
        print(f"Exp #{i+1} finished in {total_time:.2f}s")

if params["task"]=="registration":
    print("Registering data...")

    for i in range(params['numexp']):
        start_time = time()

        load_path, save_path = params["load_paths"][i], params["save_paths"][i]
        crop_start, crop_end = params["crop_start"][i], params["crop_end"][i]
        upsample_factor = params["upsample"]
        mask_crop_step = params["maskcrop"]

        make_dir(save_path)
        filelist = make_filelist(load_path, crop_start, crop_end)
        translation = get_translation(filelist, upsample_factor, mask_crop_step)
        register_frames(filelist, translation, save_path)

        total_time = time()-start_time
        print(f'Exp #{i+1} finished in {total_time:.2f}s')

code_time = time()-start
print(f"Code finished in {code_time:.2f}s")
