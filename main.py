import quadstarfiles as qsf
import matplotlib.pyplot as plt
import numpy as np
import tkinter as tk
from tkinter import ttk, Tk, filedialog
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
from pathlib import Path
from mpl_toolkits.mplot3d import Axes3D  # noqa: F401tk

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
    ax.set_box_aspect([2, 2, 1])  # Aspect ratio is set to make it more visually appealing
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

    current_cycle = tk.IntVar(value=0)
    mode = tk.StringVar(value="2D")

    def update_plot():
        # Remove all axes from the figure
        fig.clf()
        if mode.get() == "2D":
            fig.set_size_inches(15, 5)
            ax = fig.add_subplot(111)
            plot_2d(ax, cycles, current_cycle.get())
        else:
            fig.set_size_inches(17, 10)
            ax = fig.add_subplot(111, projection='3d')
            plot_3d(ax, cycles)
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

    # Entry for cycle number
    cycle_entry = ttk.Entry(cycle_frame, width=5)
    cycle_entry.pack(side=tk.LEFT, padx=5)
    cycle_entry.insert(0, "1")

    go_btn = ttk.Button(cycle_frame, text="Go", command=go_to_cycle)
    go_btn.pack(side=tk.LEFT)


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
    root.destroy()  # Destroy the hidden root before creating the plot window
    plot(cycles)
else:
    print("No file selected.")
    exit()

print(type(cycles))
#print("Cycles:", cycles)
print(type(meta))
#print("Meta:", meta)
print("Number of cycles:", len(cycles))
#print("First cycle:", cycles[0] if cycles else "No cycles found.")