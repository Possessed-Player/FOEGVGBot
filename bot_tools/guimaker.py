from tkinter import *
from tkinter import ttk
from time import sleep
from .visualobject import Vobj

class Gui:
    def __init__(self, name, sm):
        self.master = Tk()
        self.master.title(name)
        self.master.option_add("*font", ("Calibri bold", 18))
        self.machine = sm
        self.out     = []
        
    # tuple -> None
    # Parse the given command(as tuple) to one of the following:
    #   first item in tuple indicates type of control object to add
    #   which can be:   1- "options" : adds OptionMenu to the current Gui
    #                                  if the options are more than 2,
    #                                  2 RadioButton if they're 2,
    #                                  Raise an error if they're 1
    #
    #   second item should specify the control name as string
    #
    #   third item should list contents of the control object
    def add(self, *cmd):
        match cmd:
            case ("options", name, vars) if len(vars) > 2:
                var = StringVar()
                var.set(vars[0])
                opts = Frame(self.master)

                (Label(opts, text=name + ": ", anchor="w")
                        .pack(side="top", pady=5, padx=5, fill="x"))
                (OptionMenu(opts, var, *vars)
                        .pack(fill="x", expand=True, pady=5, padx=10))

                opts.pack(fill="x", pady=10)
                (ttk.Separator(self.master, orient=HORIZONTAL)
                .pack(expand=True, fill="x"))

                self.out.append(lambda: (name, var.get()))

            case ("options", name, vars) if len(vars) == 2:
                var = IntVar()
                opts = Frame(self.master)
                
                (Label(opts, text=name + ": ", anchor="w")
                    .pack(side="top", pady=5, padx=5,fill="x"))
                (Radiobutton(opts, value=0, variable=var, 
                    text=vars[0], indicatoron=0)
                .pack(side="left", fill="x", expand=True, pady=5, padx=10))
                (Radiobutton(opts, value=1, 
                    variable=var, text=vars[1], indicatoron=0)
                .pack(side="left", fill="x", expand=True, pady=5, padx=10))
                
                
                opts.pack(fill="x", pady=10)
                (ttk.Separator(self.master, orient=HORIZONTAL)
                        .pack(expand=True, fill="x"))
                
                def helper():
                    value = var.get()
                    return (name, vars[0] if value == 0 else vars[1])
                    
                self.out.append(helper)
                
    # None -> None
    # Stop the bot by mutating self.on
    def stop_bot(self):
        # Set state machine switch off
        # (will cause it to wait for already running threads to finish)
        self.machine.stop()
            
        # Restore start and stop Gui buttons
        self.spbtn["state"] = "disabled"
        self.stbtn["state"] = "normal"
            
            
    # None -> dict
    # Run the bot main function and return all the user choices in the current gui
    def run_bot(self):
        # Recalibrate the game window, in case user moved it after stopping
        Vobj.cm.recalibrate()
        
        # Prepare for starting the bot
        self.spbtn["state"] = "normal"
        self.stbtn["state"] = "disabled"
        
        self.machine.start({n:v for n, v in [f() for f in self.out]})
                
        
    # None -> None
    # Set the start, stop button at the bottom of the gui
    def _btns(self):
        btnsf = Frame(self.master)
        self.spbtn = Button(btnsf, text="STOP", 
                command=self.stop_bot, state="disabled")
        self.spbtn.pack(ipadx=10, ipady=10, 
                padx=5, pady=10, expand=True, side='left', fill="x")
        self.stbtn = Button(btnsf, text="START", 
                command=self.run_bot, width=10)
        self.stbtn.pack(ipadx=10, ipady=10, padx=5, pady=10,
                expand=True, side='left', fill="x")
        btnsf.pack(fill="x", pady=5)
        ttk.Separator(self.master, orient=HORIZONTAL).pack(expand=True, fill="x")
        
        
    # int -> None
    # Define and pack n number of status labels
    def set_status(self, n):
        if n == 0:
            return
            
        is_visible = False
        lbls = []
        svars = []

        def show_hide():
            nonlocal is_visible

            for i, lbl in enumerate(lbls):
                if lbl["text"].startswith("Status"):
                    continue
                if is_visible:
                    lbl.pack_forget()
                else:
                    lbl.pack(padx=5, pady=15,
                            fill="x")

            is_visible = not is_visible

            if is_visible:
                btn["text"] = "↑"
            else:
                btn["text"] = "↓"


        frm = Frame(self.master)
        btn = Button(frm, text="↓", command=show_hide)
        btn.pack(side="right", padx=5, pady=5)
        svars.append(StringVar())
        (Label(frm, textvariable=svars[0], 
                font=("Calibri bold", 14), anchor="w")
                .pack(side="left", padx=5, pady=5))
        frm.pack(fill="x", expand=True)

        for i in range(1, n):
            svars.append(StringVar())
            lbls.append(Label(self.master, textvariable=svars[i],
                         font=("Calibri bold", 14), anchor="w"))
        
        return svars


    def wrap_up(self, n=0):
        self._btns()
        return self.set_status(n)
        
    def show(self):
        self.master.resizable(0, 0)
        self.master.mainloop()

