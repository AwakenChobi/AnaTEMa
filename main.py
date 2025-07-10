import quadstarfiles as qsf
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
import tkinter.simpledialog
import json
from tkinter import ttk, Tk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401tk
from mass_spectra_database import NIST_MASS_SPECTRA
from datetime import datetime, timezone

################################################################################
###############################------META STRUCTURE------#######################
#meta = {
#    "general": {
#        "software_id": int,
#        "software_version": str,
#        "measure_uts": float,   # Unix timestamp of the measurement (start)
#        "author": str,
#        "n_cycles": int,        # Number of cycles
#        "n_scans": int
#    },
#    "cycles": [
#        [   # List of cycles, one entry per cycle
#            {
#                "uts": float,           # Unix timestamp for this cycle
#                "comment": str,         # Comment (may contain binary or null chars)
#                "data_format": int,
#                "fsr": float,
#                "scan_unit": str,
#                "data_unit": str
#                # ... possibly more keys ...
#            }
#        ],
#        # ... repeat for each cycle ...
#    ]
#}


################################################################################

def plot_2d(ax, cycles, cycle_idx):
    ax.clear()
    #cycles[nº_of_cycle][0: mandatory, since the data structure is [dictionary], so this cero get rid of the list]
    cycle = cycles[cycle_idx][0]
    x = cycle['Mass']
    y = cycle['Ion Current']
    ax.plot(x, y) #One could change the marker style here, e.g. 'o' for circles, 's' for squares, etc.
    ax.set_xlabel('Mass')
    ax.set_ylabel('Ion current (log scale)')
    ax.set_yscale('log')
    ax.set_title(f'Cycle {cycle_idx+1}')
    ax.grid(True, which="both", ls="--")

def plot_3d(ax, cycles):
    ax.clear()
    ax.set_box_aspect([2, 2, 1])  # Aspect ratio, the figure still looks a little small
    ax.set_xlabel('Mass')
    ax.set_ylabel('Cycle')
    ax.set_zlabel('Ion current (log scale)')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_title('All Cycles')
    ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)

    for idx, cycle_list in enumerate(cycles):
        cycle = cycle_list[0]
        x = cycle['Mass']
        y = [idx] * len(x)  # y is the cycle index, repeated for each point
        z = cycle['Ion Current']
        ax.plot(x, y, np.log10(z), color='blue')

def plot(cycles):
    root = tk.Tk()
    root.title("Mass Spectra Viewer")
    root.state('zoomed')

    fig = plt.Figure(figsize=(16, 6))
    ax = fig.add_subplot(111)
    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    # Add the Matplotlib toolbar for zoom/pan
    toolbar = NavigationToolbar2Tk(canvas, root)
    toolbar.update()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    def average_and_save_cycles():
    # Ask user for cycles to average (e.g., "1,2,3,4")
        answer = tkinter.simpledialog.askstring("Average Cycles", f"Enter cycle numbers to average (1-{len(cycles)}), comma separated:")
        if not answer:
            return
        try:
            indices = [int(i.strip()) - 1 for i in answer.split(",")]
            selected = [cycles[i][0] for i in indices]
            # Assume all cycles have the same Mass axis
            mass = selected[0]['Mass']
            ion_currents = np.array([c['Ion Current'] for c in selected])
            avg = np.mean(ion_currents, axis=0)
            std = np.std(ion_currents, axis=0)
            norm = avg / np.max(avg)
            norm_std = std / np.max(avg)
            file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if file_path:
                with open(file_path, "w") as f:
                    f.write("Mass\tAverage\tStdDev\tNormalized\n")
                    for m, a, s, n, ns in zip(mass, avg, std, norm, norm_std):
                        f.write(f"{m}\t{a}\t{s}\t{n}\t{ns}\n")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Invalid input or error: {e}")
        
    current_cycle = tk.IntVar(value=0)
    mode = tk.StringVar(value="2D")

    def save_current_cycle():
        idx = current_cycle.get()
        cycle = cycles[idx][0]
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("Mass\tIon Current\n")
                for m, ic in zip(cycle['Mass'], cycle['Ion Current']):
                    f.write(f"{m}\t{ic}\n")

    def save_all_cycles():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            # Assume all cycles have the same Mass axis
            mass = cycles[0][0]['Mass']
            n_cycles = len(cycles)
            # Collect all ion currents
            ion_currents = [cycles[i][0]['Ion Current'] for i in range(n_cycles)]
            # Write header
            with open(file_path, "w") as f: #w = writing mode
                header = "Mass\t" + "\t".join(str(i+1) for i in range(n_cycles)) + "\n"
                f.write(header)
                for i, m in enumerate(mass):
                    row = [str(m)] + [str(ion_currents[j][i]) for j in range(n_cycles)]
                    f.write("\t".join(row) + "\n")

    def update_datetime_label(meta, current_cycle):
        uts = meta["cycles"][current_cycle][0]['uts']
        dt_local = datetime.fromtimestamp(uts).astimezone()
        datetime_label.config(text=f"date/time: {dt_local.isoformat()}")

    def update_plot():
        nonlocal canvas, toolbar, fig, ax
        # Destroy the old canvas and toolbar if they exist (if this is not done, new cycles will appear all messed up)
        if hasattr(canvas, 'get_tk_widget'):
            canvas.get_tk_widget().destroy()
            update_datetime_label(meta, current_cycle.get())
        if toolbar is not None:
            toolbar.destroy()
            update_datetime_label(meta, current_cycle.get())

        # New canvas and toolbar
        if mode.get() == "2D":
            fig = plt.Figure(figsize=(15, 5))
            ax = fig.add_subplot(111)
            plot_2d(ax, cycles, current_cycle.get())
        else:
            fig = plt.Figure(figsize=(17, 10))
            ax = fig.add_subplot(111, projection='3d')
            plot_3d(ax, cycles)

        canvas = FigureCanvasTkAgg(fig, master=root)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        toolbar = NavigationToolbar2Tk(canvas, root)
        toolbar.update()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        canvas.draw()

    def next_cycle():
        if current_cycle.get() < len(cycles) - 1:
            current_cycle.set(current_cycle.get() + 1)
            update_plot()

    def prev_cycle():
        if current_cycle.get() > 0:
            current_cycle.set(current_cycle.get() - 1)
            update_plot()

    def switch_mode():
        if mode.get() == "2D":
            mode.set("3D")
            cycle_frame.pack_forget()
        else:
            mode.set("2D")
            cycle_frame.pack(side=tk.TOP, fill=tk.X)
        update_plot()

    def go_to_cycle():
        try:
            idx = int(cycle_entry.get()) - 1
            if 0 <= idx < len(cycles):
                current_cycle.set(idx)
                update_plot()
            else:
                tk.messagebox.showerror("Error", f"Cycle must be between 1 and {len(cycles)}")
        except ValueError:
            tk.messagebox.showerror("Error", "Please enter a valid integer.")


    # Controls
    control_frame = ttk.Frame(root)
    control_frame.pack(side=tk.TOP, fill=tk.X)

    switch_btn = ttk.Button(control_frame, text="Switch 2D/3D", command=switch_mode)
    switch_btn.pack(side=tk.LEFT, padx=5, pady=5)

    cycle_frame = ttk.Frame(control_frame)
    cycle_frame.pack(side=tk.LEFT, padx=5, pady=5)

    prev_btn = ttk.Button(cycle_frame, text="Previous Cycle", command=prev_cycle)
    prev_btn.pack(side=tk.LEFT)
    next_btn = ttk.Button(cycle_frame, text="Next Cycle", command=next_cycle)
    next_btn.pack(side=tk.LEFT)

    cycle_count_label = ttk.Label(control_frame, text=f"Cycles loaded: {len(cycles)}")
    cycle_count_label.pack(side=tk.LEFT, padx=10)

    dt_local = datetime.fromtimestamp(meta["cycles"][current_cycle.get()][0]['uts']).astimezone()
    datetime_label = ttk.Label(control_frame, text=f"date/time: {dt_local.isoformat()}")
    datetime_label.pack(side=tk.LEFT, padx=10)

    # Entry for cycle number
    cycle_entry = ttk.Entry(cycle_frame, width=5)
    cycle_entry.pack(side=tk.LEFT, padx=5)
    cycle_entry.insert(0, "1")

    go_btn = ttk.Button(cycle_frame, text="Go", command=go_to_cycle)
    go_btn.pack(side=tk.LEFT)

    # Slider for cycle selection
    #cycle_slider = ttk.Scale(
    #    cycle_frame,
    #    from_=1,
    #    to=len(cycles),
    #    orient='horizontal',
    #    command=lambda v: (current_cycle.set(int(float(v)) - 1), update_plot())
    #)
    #cycle_slider.pack(side=tk.LEFT, padx=5)
    #cycle_slider.set(1)

    # Save current cycle button
    save_btn = ttk.Button(control_frame, text="Save Current Cycle", command=save_current_cycle)
    save_btn.pack(side=tk.LEFT, padx=5)

    save_all_btn = ttk.Button(control_frame, text="Save All Cycles", command=save_all_cycles)
    save_all_btn.pack(side=tk.LEFT, padx=5)

    # Average/normalize cycles button
    avg_btn = ttk.Button(control_frame, text="Average/Normalize Cycles", command=average_and_save_cycles)
    avg_btn.pack(side=tk.LEFT, padx=5)

    update_plot()
    root.mainloop()

# Hide the main Tk window
root = Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select a .sac file",
    filetypes=[("SAC files", "*.sac")]
)

if file_path:
    cycles, meta = qsf.process(Path(file_path))

#Store the metadata in a JSON file:    
#    meta_file_path = filedialog.asksaveasfilename(
#    title="Save metadata as...",
#    defaultextension=".txt",
#    filetypes=[("Text files", "*.txt"), ("JSON files", "*.json")]
#)
#    if meta_file_path:
#        with open(meta_file_path, "w", encoding="utf-8") as f:
#            json.dump(meta, f, indent=2, ensure_ascii=False)
#        print(f"Metadata saved to {meta_file_path}")

    root.destroy()  # Destroy the hidden root before creating the plot window
    plot(cycles)
else:
    print("No file selected.")
    exit()