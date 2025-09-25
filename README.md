# AnaTEMa: Mass Spectra Analysis Toolkit

AnaTEMa is a Python toolkit for visualizing, analyzing, and processing mass spectrometry data from `.sac` Quadstar files. It provides a graphical user interface (GUI) for interactive exploration of mass spectra, including continuum and bar spectra, molecule evolution across cycles, and various data export and analysis tools.

---

## Features

- **Tabbed GUI** for easy navigation:
  - **Continuum Tab:** View and analyze raw mass spectra for each cycle, switch between 2D/3D views, save data, and average/normalize cycles.
  - **Bar Spectra Tab:** View bar spectra (discrete peaks) for each cycle, save data, and export all cycles.
  - **Molecule Evolution Tab:** Track the evolution of molecule intensities across cycles, filter molecules by intensity threshold, and export results.

- **Background subtraction** and conversion from continuum to bar spectra.
- **Automated molecule identification** using NIST mass spectra database and linear algebra solvers.
- **Interactive controls:** Zoom, pan, and save figures directly from the GUI.
- **Data export:** Save spectra and molecule evolution data as `.txt` files.

---

## Installation

1. Clone the repository or copy the code files to your workspace.
2. Install required Python packages:
   ```bash
   pip install numpy matplotlib
   ```
2. (option 2) run installer.bat if you do not want to install packages manually.
3. Ensure your `.sac` files and the NIST mass spectra database (`mass_spectra_database.py`) are present in the working directory.

- **Packages needed**
- numpy
- matplotlib
- tkinter
- json
- pathlib
- mpl_toolkits
- datetime
- pathlib
- requests
- bs4
- re
- os
- time

---

## Usage

Run the main GUI:
```bash
python main2_0.py
```
- On startup, select a `.sac` file when prompted.
- The GUI will open with three tabs for different analysis modes.

---

## File Overview

### `main.py`
- **Main GUI application.**
- Loads `.sac` files, processes cycles, and launches the tabbed interface.
- Contains functions for plotting, saving, and navigating spectra and molecule data.
- 3D view of all the cycles loaded.

### `main2_0.py`
- **Main GUI application.**
- Loads `.sac` files, processes cycles, and launches the tabbed interface.
- Contains functions for plotting, saving, and navigating spectra and molecule data.
- Allows to visualize molecule concentration evolution vs cycle.

### `Continuum_to_bar_spectra.py`
- **Function:** `continuum_to_bar_spectra(x, y, database)`
- Converts continuum spectra to bar spectra by subtracting background (assuming e^-x background, please check if your spectra fits with these characteristics) and extracting peak intensities.
- Returns mass/charge peaks, bar intensities, and normalized intensities.

### `solver.py`
- **Function:** `NNLS_solver_mass_spectra(normalized_bar_spectra, NIST_MASS_SPECTRA)`
- Solves for molecule concentrations using linear algebra (non negative least squares).
- Handles singular matrices and returns molecule intensities.

### `mass_spectra_database.py`
- Contains the NIST mass spectra database as Python dictionaries/lists.
- Each molecule is represented by a list of intensities for each mass/charge peak.

### `searcher.py`
- Tools for analyzing the database:
  - Finds isolated, pair, and multi-molecule peak contributions.
  - It simply selects the maximum value between a range.
  - Prints summary statistics and distribution of contributors per peak.

---

## GUI Tabs & Controls

### **Continuum Tab**
- **Cycle navigation:** Next/Previous/Go to cycle.
- **2D/3D switch:** Toggle between single cycle and all cycles view (only available in main.py).
- **Save:** Export current or all cycles.
- **Average/Normalize:** Select cycles to average and normalize.

### **Bar Spectra Tab**
- **Cycle navigation:** Next/Previous/Go to cycle.
- **Save:** Export current or all bar spectra.

### **Molecule Evolution Tab**
- **Plot:** Shows molecule intensities per cycle (filtered by threshold).
- **Save:** Export all molecule evolution data (including those below threshold).
- **Legend:** Only molecules above threshold appear in the legend.

---

## Advanced Analysis

- **Background plotting:** Optionally plot the computed background in a new window for inspection.
- **Peak contribution analysis:** Use `searcher.py` to find which molecules contribute to each peak and identify isolated or overlapping peaks.

---

## Customization

- **Thresholds:** Adjust intensity thresholds for filtering molecules in the evolution plot.
- **Bar width:** Change bar width in bar spectra for better visualization.
- **Colormaps and styles:** Easily modify colors and line styles for clearer plots.

---

## Troubleshooting

- **Matrix errors:** Ensure all molecule spectra in the database have the same length as the mass/charge peaks.
- **GUI controls:** If controls are not visible, check that they are packed into the correct parent frame before the plot canvas.
- **Color repetition:** Use larger colormaps and cycle through line styles for better distinction.

---

## Future work

- **Adapt algorithm to different length input data:** The NIST database should be increased and the code should adapt the range of molecules that is used (right now, molecules with main peak above 52 a.m.u will not be considered).

- **Include 3D plot in main2_0.py:** Right now, the most complete version of the code is the 2_0 version, included in this folder. However, for technical issues, 3D plot is not available in this version but it is in main.py. At some point, this functionality should be merged to the latest version.
 
## Credits

Developed by Antonio Cobos Luque (Universidad de Córdoba).

Uses NIST mass spectra data and standard Python scientific libraries.

Collaborators:
- Alexhall: mentoring
- Rocío Pérez: testing

**Cite as:** Cobos-Luque, A., AnaTEMa (2025). https://github.com/AwakenChobi/AnaTEMa

**Or**: Download cite.bib and add it to your text editor.

---


## License

MIT License (or specify your license here).
