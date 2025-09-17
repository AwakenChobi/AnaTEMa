import numpy as np
import quadstarfiles as qsf
import matplotlib.pyplot as plt
import tkinter as tk
import itertools
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
from pathlib import Path
from mass_spectra_database import NIST_MASS_SPECTRA # Database in this folder
from solver import NNLS_solver_mass_spectra_etanol ## Function in this folder
from continuum_to_bar_spectra import continuum_to_bar_spectra #Function in this folder
from datetime import datetime

########################################################################
#######################------META STRUCTURE------#######################
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


#######################################################################


def plot_gui(cycles, meta):
    root = tk.Tk()
    root.title("Mass Spectra Viewer")
    root.state('zoomed')

    def open_new_sac():
        file_path = filedialog.askopenfilename(
            title="Select a .sac file",
            filetypes=[("SAC files", "*.sac")]
        )
        if file_path:
            new_cycles, new_meta = qsf.process(Path(file_path))
            root.destroy()
            plot_gui(new_cycles, new_meta)

    # Add menu for opening new .sac file
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open .sac file", command=open_new_sac)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    root.config(menu=menubar)

    notebook = ttk.Notebook(root)
    notebook.pack(fill=tk.BOTH, expand=1)

    # --- Tab 1: Continuum ---
    frame_cont = ttk.Frame(notebook)
    notebook.add(frame_cont, text="Continuum")

    fig1 = plt.Figure(figsize=(15, 5))
    ax1 = fig1.add_subplot(111)
    canvas1 = FigureCanvasTkAgg(fig1, master=frame_cont)
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    toolbar1 = NavigationToolbar2Tk(canvas1, frame_cont)
    toolbar1.update()
    canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    control_frame1 = ttk.Frame(frame_cont)
    control_frame1.pack(side=tk.TOP, fill=tk.X)

    # State variables
    current_cycle = tk.IntVar(value=0)
    mode = tk.StringVar(value="2D")

    # --- Tab 2: Bar Spectra ---
    frame_bar = ttk.Frame(notebook)
    notebook.add(frame_bar, text="Bar Spectra")

    fig2 = plt.Figure(figsize=(15, 5))
    ax2 = fig2.add_subplot(111)
    canvas2 = FigureCanvasTkAgg(fig2, master=frame_bar)
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=1)
    toolbar2 = NavigationToolbar2Tk(canvas2, frame_bar)
    toolbar2.update()
    canvas2.get_tk_widget().pack(fill=tk.BOTH, expand=1)

    control_frame2 = ttk.Frame(frame_bar)
    control_frame2.pack(side=tk.TOP, fill=tk.X)

    current_cycle_bar = tk.IntVar(value=0)

    # --- Tab 3: Molecule Evolution ---
    frame_mol = ttk.Frame(notebook)
    notebook.add(frame_mol, text="Molecule Evolution")


    control_frame3 = ttk.Frame(frame_mol)
    control_frame3.pack(side=tk.BOTTOM, fill=tk.X)

    fig3 = plt.Figure(figsize=(16, 8))
    ax3 = fig3.add_subplot(111)
    canvas3 = FigureCanvasTkAgg(fig3, master=frame_mol)
    toolbar3 = NavigationToolbar2Tk(canvas3, frame_mol)
    toolbar3.update()
    toolbar3.pack(side=tk.BOTTOM, fill=tk.X)
    canvas3.get_tk_widget().pack(side=tk.BOTTOM, fill=tk.BOTH, expand=1)

    # --- Functions for Tab 1 (Continuum) ---
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

    def update_datetime_label1():
        uts = meta["cycles"][current_cycle.get()][0]['uts']
        dt_local = datetime.fromtimestamp(uts).astimezone()
        datetime_label1.config(text=f"date/time: {dt_local.isoformat()}")

    def update_plot1():
        nonlocal canvas1, toolbar1, fig1, ax1

        # if hasattr(canvas1, 'get_tk_widget'):
        #     canvas1.get_tk_widget().destroy()
        #     update_datetime_label1()
        # if toolbar1 is not None:
        #     toolbar1.destroy()
        #     update_datetime_label1()

        # if mode.get() == "2D":
        #     fig1 = plt.Figure(figsize=(15, 5))
        #     ax1 = fig1.add_subplot(111)
        #     plot_2d(ax1, cycles, current_cycle.get())
        # else:
        #     fig1 = plt.Figure(figsize=(17, 10))
        #     ax1 = fig1.add_subplot(111, projection='3d')
        #     plot_3d(ax1, cycles)

        if mode.get() == "2D":
            ax1.clear()
            plot_2d(ax1, cycles, current_cycle.get())
        else:
            ax1.clear()
            plot_3d(ax1, cycles)
        canvas1.draw()
        update_datetime_label1()

        # canvas1 = FigureCanvasTkAgg(fig1, master=root)
        # canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        # toolbar1 = NavigationToolbar2Tk(canvas1, root)
        # toolbar1.update()
        # canvas1.get_tk_widget().pack(fill=tk.BOTH, expand=1)
        # canvas1.draw()

    def next_cycle1():
        if current_cycle.get() < len(cycles) - 1:
            current_cycle.set(current_cycle.get() + 1)
            update_plot1()

    def prev_cycle1():
        if current_cycle.get() > 0:
            current_cycle.set(current_cycle.get() - 1)
            update_plot1()

    # def switch_mode1():
    #     if mode.get() == "2D":
    #         mode.set("3D")
    #         cycle_frame1.pack_forget()
    #     else:
    #         mode.set("2D")
    #         cycle_frame1.pack(side=tk.TOP, fill=tk.X)
    #     update_plot1()

    def go_to_cycle1():
        try:
            idx = int(cycle_entry1.get()) - 1
            if 0 <= idx < len(cycles):
                current_cycle.set(idx)
                update_plot1()
            else:
                messagebox.showerror("Error", f"Cycle must be between 1 and {len(cycles)}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def save_current_cycle1():
        idx = current_cycle.get()
        cycle = cycles[idx][0]
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("Mass\tIon Current\n")
                for m, ic in zip(cycle['Mass'], cycle['Ion Current']):
                    f.write(f"{m}\t{ic}\n")

    def save_all_cycles1():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            # Assume all cycles have the same Mass axis
            mass = cycles[0][0]['Mass']
            n_cycles = len(cycles)
            # Collect all ion currents
            ion_currents = [cycles[i][0]['Ion Current'] for i in range(n_cycles)]
            with open(file_path, "w") as f:
                header = "Mass\t" + "\t".join(str(i+1) for i in range(n_cycles)) + "\n"
                f.write(header)
                for i, m in enumerate(mass):
                    row = [str(m)] + [str(ion_currents[j][i]) for j in range(n_cycles)]
                    f.write("\t".join(row) + "\n")

    def average_and_save_cycles1():
        # Ask user for cycles to average (e.g., "1,2,3,4")
        answer = tk.simpledialog.askstring("Average Cycles", f"Enter cycle numbers to average (1-{len(cycles)}), comma separated:")
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
            messagebox.showerror("Error", f"Invalid input or error: {e}")

    # Controls for Tab 1
#    switch_btn1 = ttk.Button(control_frame1, text="Switch 2D/3D", command=switch_mode1)
#    switch_btn1.pack(side=tk.LEFT, padx=5, pady=5)

    cycle_frame1 = ttk.Frame(control_frame1)
    cycle_frame1.pack(side=tk.LEFT, padx=5, pady=5)

    prev_btn1 = ttk.Button(cycle_frame1, text="Previous Cycle", command=prev_cycle1)
    prev_btn1.pack(side=tk.LEFT)
    next_btn1 = ttk.Button(cycle_frame1, text="Next Cycle", command=next_cycle1)
    next_btn1.pack(side=tk.LEFT)

    cycle_count_label1 = ttk.Label(control_frame1, text=f"Cycles loaded: {len(cycles)}")
    cycle_count_label1.pack(side=tk.LEFT, padx=10)

    dt_local = datetime.fromtimestamp(meta["cycles"][current_cycle.get()][0]['uts']).astimezone()
    datetime_label1 = ttk.Label(control_frame1, text=f"date/time: {dt_local.isoformat()}")
    datetime_label1.pack(side=tk.LEFT, padx=10)

    # Entry for cycle number
    cycle_entry1 = ttk.Entry(cycle_frame1, width=5)
    cycle_entry1.pack(side=tk.LEFT, padx=5)
    cycle_entry1.insert(0, "1")

    go_btn1 = ttk.Button(cycle_frame1, text="Go", command=go_to_cycle1)
    go_btn1.pack(side=tk.LEFT)

    # Save current cycle button
    save_btn1 = ttk.Button(control_frame1, text="Save Current Cycle", command=save_current_cycle1)
    save_btn1.pack(side=tk.LEFT, padx=5)

    save_all_btn1 = ttk.Button(control_frame1, text="Save All Cycles", command=save_all_cycles1)
    save_all_btn1.pack(side=tk.LEFT, padx=5)

    # Average/normalize cycles button
    avg_btn1 = ttk.Button(control_frame1, text="Average/Normalize Cycles", command=average_and_save_cycles1)
    avg_btn1.pack(side=tk.LEFT, padx=5)

    update_plot1()

    # --- Functions for Tab 2 (Bar Spectra) ---
    def plot_bar_spectrum(ax, cycles, cycle_idx):
        ax.clear()
        cycle = cycles[cycle_idx][0]
        x = cycle['Mass']
        y = cycle['Ion Current']
        x_bars, y_bars, norm_y_bars = continuum_to_bar_spectra(x, y, NIST_MASS_SPECTRA)
        ax.bar(x_bars, y_bars, width=0.5)
        ax.set_xlabel('Mass/Charge')
        ax.set_ylabel('Ion current (log scale)')
        ax.set_yscale('log')
        ax.set_title(f'Bar Spectrum (Cycle {cycle_idx+1})')
        ax.grid(True, which="both", ls="--")

    def update_plot2():
        fig2.clf()
        ax = fig2.add_subplot(111)
        plot_bar_spectrum(ax, cycles, current_cycle_bar.get())
        canvas2.draw()

    def save_current_cycle2():
        idx = current_cycle_bar.get()
        cycle = cycles[idx][0]
        x_bars, y_bars, norm_y_bars = continuum_to_bar_spectra(cycle['Mass'], cycle['Ion Current'], NIST_MASS_SPECTRA)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("Mass\tIon Current\tNormalized\n")
                for m, ic, nc in zip(x_bars, y_bars, norm_y_bars):
                    f.write(f"{m}\t{ic}\t{nc}\n")

    def save_all_cycles2():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            # Assume all cycles have the same Mass axis
            mass = NIST_MASS_SPECTRA['Mass']
            n_cycles = len(cycles)
            ion_currents = [cycles[i][0]['Ion Current'] for i in range(n_cycles)]
            with open(file_path, "w") as f:
                header = "Mass\t" + "\t".join(str(i+1) for i in range(n_cycles)) + "\n"
                f.write(header)
                for i, m in enumerate(mass):
                    row = [str(m)] + [str(ion_currents[j][i]) for j in range(n_cycles)]
                    f.write("\t".join(row) + "\n")

    def next_cycle2():
        if current_cycle_bar.get() < len(cycles) - 1:
            current_cycle_bar.set(current_cycle_bar.get() + 1)
            update_plot2()

    def prev_cycle2():
        if current_cycle_bar.get() > 0:
            current_cycle_bar.set(current_cycle_bar.get() - 1)
            update_plot2()

    def go_to_cycle2():
        try:
            idx = int(cycle_entry2.get()) - 1
            if 0 <= idx < len(cycles):
                current_cycle_bar.set(idx)
                update_plot2()
            else:
                messagebox.showerror("Error", f"Cycle must be between 1 and {len(cycles)}")
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    # Controls for Tab 2
    cycle_frame2 = ttk.Frame(control_frame2)
    cycle_frame2.pack(side=tk.LEFT, padx=5, pady=5)

    prev_btn2 = ttk.Button(cycle_frame2, text="Previous Cycle", command=prev_cycle2)
    prev_btn2.pack(side=tk.LEFT)
    next_btn2 = ttk.Button(cycle_frame2, text="Next Cycle", command=next_cycle2)
    next_btn2.pack(side=tk.LEFT)

    cycle_count_label2 = ttk.Label(control_frame2, text=f"Cycles loaded: {len(cycles)}")
    cycle_count_label2.pack(side=tk.LEFT, padx=10)

    cycle_entry2 = ttk.Entry(cycle_frame2, width=5)
    cycle_entry2.pack(side=tk.LEFT, padx=5)
    cycle_entry2.insert(0, "1")

    go_btn2 = ttk.Button(cycle_frame2, text="Go", command=go_to_cycle2)
    go_btn2.pack(side=tk.LEFT)

    # Save current cycle button
    save_btn2 = ttk.Button(control_frame2, text="Save Current Cycle", command=save_current_cycle2)
    save_btn2.pack(side=tk.LEFT, padx=5)

    save_all_btn2 = ttk.Button(control_frame2, text="Save All Cycles", command=save_all_cycles2)
    save_all_btn2.pack(side=tk.LEFT, padx=5)

    update_plot2()

    # --- Tab 3: Molecule Evolution ---
    molecule_names = [name for name in NIST_MASS_SPECTRA.keys() if name != 'Mass/Charge peaks']
    n_cycles = len(cycles)
    intensities = np.zeros((len(molecule_names), n_cycles))
    print(f'Dimensions of intensities array: {intensities.shape}')
    print(f'type of intensities: {type(intensities[0,0])}')
    for idx, cycle_list in enumerate(cycles):
        cycle = cycle_list[0]
        x = cycle['Mass']
        y = cycle['Ion Current']
        _, _, normalized_y_bars = continuum_to_bar_spectra(x, y, NIST_MASS_SPECTRA)
        result = NNLS_solver_mass_spectra_etanol(normalized_y_bars, NIST_MASS_SPECTRA)
        intensities[:, idx] = [result[name] for name in molecule_names]

    plot_indices = [i for i in range(len(molecule_names)) if np.any(intensities[i, :] > 1e-7)]
    plot_names = [molecule_names[i] for i in plot_indices]
    num_lines = len(plot_indices)
    color_map = plt.cm.get_cmap('tab20', num_lines)
    style_list = ['-', '--', '-.', ':']

    combinations = list(itertools.product(range(num_lines), style_list))
    ax3.clear()
    for idx, (i, name) in enumerate(zip(plot_indices, plot_names)):
        color_idx, style = combinations[idx % len(combinations)]
        color = color_map(color_idx)
        ax3.plot(
            range(1, n_cycles+1),
            intensities[i, :],
            label=name,
            color=color,
            linestyle=style,
            linewidth=2
        )
    
    def save_molecule_evolution():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                f.write("Molecule\t" + "\t".join(f"Cycle_{i+1}" for i in range(n_cycles)) + "\n")
                for i, name in enumerate(molecule_names):
                    row = [name] + [str(intensities[i, j]) for j in range(n_cycles)]
                    f.write("\t".join(row) + "\n")

    ax3.set_xlabel('Cycle')
    ax3.set_ylabel('Intensity')
    ax3.set_yscale('log')
    ax3.set_title('Molecule Evolution')
    ax3.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), fontsize='small', ncol=1)
    ax3.grid(True)

    save_evolution_btn = ttk.Button(control_frame3, text="Save Molecule Evolution Data", command=save_molecule_evolution)
    save_evolution_btn.pack(side=tk.TOP, padx=5, pady=5)

    canvas3.draw()

    root.mainloop()

# --- File dialog and data loading ---
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select a .sac file",
    filetypes=[("SAC files", "*.sac")]
)
if file_path:
    cycles, meta = qsf.process(Path(file_path))
    root.destroy()
    plot_gui(cycles, meta)
else:
    print("No file selected.")
    exit()