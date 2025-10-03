import numpy as np
import quadstarfiles as qsf
import matplotlib.pyplot as plt
import tkinter as tk
import itertools
from tkinter import ttk, filedialog, messagebox
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.ticker import MaxNLocator
from pathlib import Path
from database import ADJUSTED_NIST_MASS_SPECTRA # Database in this folder
from solver import NNLS_solver_mass_spectra ## Function in this folder
from continuum_to_bar_spectra import continuum_to_bar_spectra #Function in this folder
from datetime import datetime
import threading
import time

def show_loading_window():
    """Create and show loading window with progress bar"""
    loading_window = tk.Toplevel()
    loading_window.title("Loading AnaTEMa")
    loading_window.geometry("400x100")
    loading_window.resizable(False, False)
    
    # Center the window
    loading_window.update_idletasks()
    x = (loading_window.winfo_screenwidth() // 2) - (400 // 2)
    y = (loading_window.winfo_screenheight() // 2) - (100 // 2)
    loading_window.geometry(f"400x100+{x}+{y}")
    
    loading_label = ttk.Label(loading_window, text="Loading mass spectra data...")
    loading_label.pack(pady=10)
    
    progress = ttk.Progressbar(loading_window, mode='indeterminate', length=300)
    progress.pack(pady=10)
    progress.start(10)
    
    return loading_window, progress

def process_file_with_loading(file_path, root):
    """Process file and show loading bar"""
    loading_window, progress = show_loading_window()
    
    def process_in_thread():
        try:
            if file_path.lower().endswith('.sac'):
                # Process SAC file
                cycles, meta = qsf.process(Path(file_path))
            elif file_path.lower().endswith('.txt'):
                # Process TXT file
                cycles, meta = process_txt_file(file_path)
            else:
                raise ValueError("Unsupported file format")
            
            # Close loading window and start main GUI
            def success_callback():
                progress.stop()
                loading_window.destroy()
                root.destroy()
                plot_gui(cycles, meta)
            
            loading_window.after(0, success_callback)
            
        except Exception as e:
            # Capture the error message
            error_msg = str(e)
            
            def error_callback():
                progress.stop()
                loading_window.destroy()
                messagebox.showerror("Error", f"Failed to load file: {error_msg}")
                root.destroy()
            
            loading_window.after(0, error_callback)
    
    # Start processing in separate thread
    thread = threading.Thread(target=process_in_thread)
    thread.daemon = True
    thread.start()
    
    return loading_window

def process_txt_file(file_path):
    # Compatibility with cycles stored in .txt files. This function adapts the data to be compatible with the rest of the code.

    """
    Process .txt file with format:
    - First row (ignoring first element): cycle numbers
    - First column (ignoring first element): x coordinates (mass values)
    - Rest: intensities for each x value in respective cycle
    """

    data = np.loadtxt(file_path, delimiter='\t', skiprows=1)
    
    mass_values = data[:, 0]
    
    intensities = data[:, 1:]
    
    n_cycles = intensities.shape[1]
    
    cycles = []
    for cycle_idx in range(n_cycles):
        cycle_data = {
            'Mass': mass_values,
            'Ion Current': intensities[:, cycle_idx],
            'uts': 'N/A',
        }
        cycles.append([cycle_data])  # Wrap in list to match expected structure
    
    # Create metadata structure
    meta = {
        "general": {
            "software_id": -1,
            "software_version": "TXT Import",
            "measure_uts": datetime.now().timestamp(),
            "author": "N/A",
            "n_cycles": n_cycles,
            "n_scans": len(mass_values)
        },
        "cycles": []
    }
    
    # Create cycle metadata
    for cycle_idx in range(n_cycles):
        cycle_meta = [{
            "uts": datetime.now().timestamp() + cycle_idx,
            "comment": f"Imported from TXT file - Cycle {cycle_idx + 1}",
            "data_format": -1,
            "fsr": -1,
            "scan_unit": "m/z",
            "data_unit": "Ion Current"
        }]
        meta["cycles"].append(cycle_meta)
    
    return cycles, meta

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
    max_mass = int(np.max(cycles[0][0]['Mass'])+1)
    NIST_MASS_SPECTRA = ADJUSTED_NIST_MASS_SPECTRA(max_mass)

    root = tk.Tk()
    root.title("Mass Spectra Viewer")
    root.state('zoomed')

    def open_new_sac():
        file_path = filedialog.askopenfilename(
            title="Select a .sac or .txt file",
            filetypes=[("SAC files", "*.sac"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if file_path:
            if file_path.lower().endswith('.sac') or file_path.lower().endswith('.txt'):
                process_file_with_loading(file_path, root)
            else:
                messagebox.showerror("Error", "Please select a valid .sac or .txt file.")
                return

    # Add menu for opening new file
    menubar = tk.Menu(root)
    filemenu = tk.Menu(menubar, tearoff=0)
    filemenu.add_command(label="Open file (.sac/.txt)", command=open_new_sac)
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
        cycle = cycles[cycle_idx][0]
        x = cycle['Mass']
        y = cycle['Ion Current']
        ax.plot(x, y)
        ax.set_xlabel('Mass')
        ax.set_ylabel('Ion current (log scale)')
        ax.set_yscale('log')
        ax.set_title(f'Cycle {cycle_idx+1}')
        ax.grid(True, which="both", ls="--")

    def plot_3d(ax, cycles):
        ax.clear()
        ax.set_box_aspect([2, 2, 1])
        ax.set_xlabel('Mass')
        ax.set_ylabel('Cycle')
        ax.set_zlabel('Ion current (log scale)')
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))
        ax.set_title('All Cycles')
        ax.grid(True, linestyle=':', linewidth=0.5, alpha=0.3)

        for idx, cycle_list in enumerate(cycles):
            cycle = cycle_list[0]
            x = cycle['Mass']
            y = [idx] * len(x)
            z = cycle['Ion Current']
            ax.plot(x, y, np.log10(z), color='blue')

    def update_datetime_label1():
        uts = meta["cycles"][current_cycle.get()][0]['uts']
        dt_local = datetime.fromtimestamp(uts).astimezone()
        datetime_label1.config(text=f"date/time: {dt_local.isoformat()}")

    def update_plot1():
        if mode.get() == "2D":
            ax1.clear()
            plot_2d(ax1, cycles, current_cycle.get())
        else:
            ax1.clear()
            plot_3d(ax1, cycles)
        canvas1.draw()
        update_datetime_label1()

    def next_cycle1():
        if current_cycle.get() < len(cycles) - 1:
            current_cycle.set(current_cycle.get() + 1)
            update_plot1()

    def prev_cycle1():
        if current_cycle.get() > 0:
            current_cycle.set(current_cycle.get() - 1)
            update_plot1()

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
            mass = cycles[0][0]['Mass']
            n_cycles = len(cycles)
            ion_currents = [cycles[i][0]['Ion Current'] for i in range(n_cycles)]
            with open(file_path, "w") as f:
                header = "Mass\t" + "\t".join(str(i+1) for i in range(n_cycles)) + "\n"
                f.write(header)
                for i, m in enumerate(mass):
                    row = [str(m)] + [str(ion_currents[j][i]) for j in range(n_cycles)]
                    f.write("\t".join(row) + "\n")

    def average_and_save_cycles1():
        answer = tk.simpledialog.askstring("Average Cycles", f"Enter cycle numbers to average (1-{len(cycles)}), comma separated:")
        if not answer:
            return
        try:
            indices = [int(i.strip()) - 1 for i in answer.split(",")]
            selected = [cycles[i][0] for i in indices]
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

    cycle_entry1 = ttk.Entry(cycle_frame1, width=5)
    cycle_entry1.pack(side=tk.LEFT, padx=5)
    cycle_entry1.insert(0, "1")

    go_btn1 = ttk.Button(cycle_frame1, text="Go", command=go_to_cycle1)
    go_btn1.pack(side=tk.LEFT)

    save_btn1 = ttk.Button(control_frame1, text="Save Current Cycle", command=save_current_cycle1)
    save_btn1.pack(side=tk.LEFT, padx=5)

    save_all_btn1 = ttk.Button(control_frame1, text="Save All Cycles", command=save_all_cycles1)
    save_all_btn1.pack(side=tk.LEFT, padx=5)

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
                f.write("Mass\tBar Intensity\tNormalized\n")
                for m, ic, nc in zip(x_bars, y_bars, norm_y_bars):
                    f.write(f"{m}\t{ic}\t{nc}\n")

    def save_all_cycles2():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            mass = NIST_MASS_SPECTRA['Mass/Charge peaks']
            n_cycles = len(cycles)
            with open(file_path, "w") as f:
                header = "Mass\t" + "\t".join(str(i+1) for i in range(n_cycles)) + "\n"
                f.write(header)
                for i, m in enumerate(mass):
                    row = [str(m)]
                    for j in range(n_cycles):
                        cycle = cycles[j][0]
                        x_bars, y_bars, _ = continuum_to_bar_spectra(cycle['Mass'], cycle['Ion Current'], NIST_MASS_SPECTRA)
                        row.append(str(y_bars[i]))
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
        result = NNLS_solver_mass_spectra(normalized_y_bars, NIST_MASS_SPECTRA)
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
        # color_idx = combinations_color[idx % len(combinations_color)][1]
        color = color_map(idx)
        ax3.plot(
            range(1, n_cycles+1),
            intensities[i, :],
            label=name,
            color=color,
            linestyle=style,
            linewidth=2
        )

    ax3.set_xlabel('Cycle')
    ax3.set_ylabel('Intensity')
    ax3.set_yscale('log')
    ax3.set_title('Molecule Evolution')
    ax3.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), fontsize='small', ncol=1)
    ax3.grid(True)
    
    def save_molecule_evolution():
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as f:
                # Get the currently displayed molecules from the plot
                current_labels = [line.get_label() for line in ax3.get_lines()]
                
                if not current_labels:
                    # If no plot is shown, use all original molecules
                    f.write("Molecule\t" + "\t".join(f"Cycle_{i+1}" for i in range(n_cycles)) + "\n")
                    for i, name in enumerate(molecule_names):
                        row = [name] + [str(intensities[i, j]) for j in range(n_cycles)]
                        f.write("\t".join(row) + "\n")
                else:
                    # Save only the currently displayed molecules
                    f.write("Molecule\t" + "\t".join(f"Cycle_{i+1}" for i in range(n_cycles)) + "\n")
                    
                    # Get the data for each currently displayed molecule
                    for line in ax3.get_lines():
                        molecule_name = line.get_label()
                        y_data = line.get_ydata()  # Get the intensity data from the plot
                        
                        # Write the molecule name and its cycle data
                        row = [molecule_name] + [str(intensity) for intensity in y_data]
                        f.write("\t".join(row) + "\n")

    def open_compounds_window():
        new_window = tk.Toplevel(root)
        new_window.title("Select Compounds")
        new_window.geometry("400x600")

        # Search frame at the top
        search_frame = ttk.Frame(new_window)
        search_frame.pack(fill="x", padx=10, pady=5)
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side="left", padx=5, fill="x", expand=True)

        # Scrollbar container
        container = ttk.Frame(new_window)
        container.pack(fill="both", expand=True, padx=10, pady=5)

        canvas = tk.Canvas(container)
        scrollbar = ttk.Scrollbar(container, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # List of compounds
        compounds = [name for name in NIST_MASS_SPECTRA.keys() if name != 'Mass/Charge peaks']

        # Keep track of the checkbox variables and widgets
        all_checkboxes = []
        variables = []

        # Create checkboxes for all compounds
        for compound in compounds:
            var = tk.BooleanVar(value=True)
            chk = ttk.Checkbutton(scrollable_frame, text=compound, variable=var)
            chk.pack(anchor="w", padx=10, pady=2)
            variables.append((compound, var))
            all_checkboxes.append((compound, var, chk))

        # Search function
        def search_compounds(*args):
            search_text = search_var.get().lower()
            
            # Hide all checkboxes first
            for compound, var, chk in all_checkboxes:
                chk.pack_forget()
            
            # Show only matching checkboxes
            for compound, var, chk in all_checkboxes:
                if search_text in compound.lower():
                    chk.pack(anchor="w", padx=10, pady=2)
            
            # Update canvas scroll region
            scrollable_frame.update_idletasks()
            canvas.configure(scrollregion=canvas.bbox("all"))

        # Bind search function to entry changes
        search_var.trace("w", search_compounds)

        # Buttons frame
        buttons_frame = ttk.Frame(new_window)
        buttons_frame.pack(fill="x", padx=10, pady=5)

        # Select/Deselect all buttons
        def select_all():
            for compound, var, chk in all_checkboxes:
                # Only select visible checkboxes
                if chk.winfo_manager():  # Check if widget is packed/visible
                    var.set(True)

        def deselect_all():
            for compound, var, chk in all_checkboxes:
                # Only deselect visible checkboxes
                if chk.winfo_manager():  # Check if widget is packed/visible
                    var.set(False)

        select_all_btn = ttk.Button(buttons_frame, text="Select All Visible", command=select_all)
        select_all_btn.pack(side="left", padx=5)

        deselect_all_btn = ttk.Button(buttons_frame, text="Deselect All Visible", command=deselect_all)
        deselect_all_btn.pack(side="left", padx=5)

        # Function to update the equation (same as before)
        def update_equation():
            selected = [c for c, v in variables if v.get()]
            filtered_molecules = {name: NIST_MASS_SPECTRA[name] for name in selected}
            n_cycles = len(cycles)
            intensities = np.zeros((len(selected), n_cycles))
            for idx, cycle_list in enumerate(cycles):
                cycle = cycle_list[0]
                x = cycle['Mass']
                y = cycle['Ion Current']
                _, _, normalized_y_bars = continuum_to_bar_spectra(x, y, NIST_MASS_SPECTRA)
                filtered_molecules['Mass/Charge peaks'] = NIST_MASS_SPECTRA['Mass/Charge peaks']
                result = NNLS_solver_mass_spectra(normalized_y_bars, filtered_molecules)
                intensities[:, idx] = [result[name] for name in selected]
            plot_indices = [i for i in range(len(selected)) if np.any(intensities[i, :] > 1e-7)]
            plot_names = [selected[i] for i in plot_indices]
            ax3.clear()
            combinations = list(itertools.product(range(num_lines), style_list))
            for idx, (i, name) in enumerate(zip(plot_indices, plot_names)):
                color_idx, style = combinations[idx % len(combinations)]
                color = color_map(idx)
                ax3.plot(
                    range(1, n_cycles+1),
                    intensities[i, :],
                    label=name,
                    color=color,
                    linestyle=style,
                    linewidth=2
                )

            ax3.legend()
            ax3.set_xlabel('Cycle')
            ax3.set_ylabel('Intensity')
            ax3.set_yscale('log')
            ax3.set_title('Molecule Evolution')
            ax3.legend(loc='upper right', bbox_to_anchor=(1.15, 1.0), fontsize='small', ncol=1)
            ax3.grid(True)
            canvas3.draw()
            new_window.destroy()  # Close window after updating

        # OK button
        ok_btn = ttk.Button(buttons_frame, text="OK", command=update_equation)
        ok_btn.pack(side="right", padx=5)

        # Focus on search entry for immediate typing
        search_entry.focus()

    save_evolution_btn = ttk.Button(control_frame3, text="Save Molecule Evolution Data", command=save_molecule_evolution)
    save_evolution_btn.pack(side=tk.TOP, padx=5, pady=5)

    little_box_btn = ttk.Button(control_frame3, text="Molecules considered", command=open_compounds_window)
    little_box_btn.pack(side=tk.TOP, padx=5, pady=5)

    canvas3.draw()

    root.mainloop()

# --- File dialog and data loading with loading bar ---
root = tk.Tk()
root.withdraw()
file_path = filedialog.askopenfilename(
    title="Select a .sac or .txt file",
    filetypes=[("SAC files", "*.sac"), ("Text files", "*.txt"), ("All files", "*.*")]
)

if file_path:
    # Show loading bar and process file
    loading_window = process_file_with_loading(file_path, root)
    root.mainloop() 
else:
    print("No file selected.")
    root.destroy()
    exit()