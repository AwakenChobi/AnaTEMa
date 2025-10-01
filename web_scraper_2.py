import requests
from bs4 import BeautifulSoup
import re
import os
import time

def get_molecule_ids_and_names(search_url):
    resp = requests.get(search_url)
    soup = BeautifulSoup(resp.text, "html.parser")
    ids_and_names = []
    for a in soup.find_all("a", href=True):
        href = a["href"]
        match = re.search(r'ID=(C\d+)', href)
        if match:
            mol_id = match.group(1)
            name = a.text.strip()
            ids_and_names.append((name, mol_id))
    return ids_and_names

def parse_jcamp_peak_table(filepath):
    with open(filepath, encoding="utf-8") as f:
        lines = f.readlines()
    in_table = False
    pairs = []
    for line in lines:
        if "##PEAK TABLE=(XY..XY)" in line:
            in_table = True
            continue
        if "##END=" in line:
            break
        if in_table:
            for pair in line.strip().split():
                if ',' in pair:
                    x, y = pair.split(',')
                    y = y.zfill(4)  # Asegura que tiene al menos 4 cifras
                    y_float = float(y[:-2] + '.' + y[-2:])
                    pairs.append((int(x), y_float))
    return pairs

def normalize_and_format(mol_name, mz_int, max_mz=78):
    if not mz_int:
        return None, None
    max_int = max(i for _, i in mz_int)
    arr = [0.0] * max_mz
    for mz, inten in mz_int:
        idx = mz - 2  # m/z=2 corresponde a idx=0
        if 0 <= idx < max_mz:
            arr[idx] = inten / max_int
    pyname = re.sub(r'\W|^(?=\d)', '_', mol_name.lower())
    return pyname, arr

def write_mass_spectra_database(output_file, molecules_data, max_mz):
    """Write the mass spectra database to a Python file"""
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("# Mass Spectra Database\n")
        f.write("# Generated automatically from NIST WebBook\n")
        f.write(f"# Maximum m/z considered: {max_mz + 1}\n\n")
        
        # Write individual molecule spectra
        for mol_name, pyname, spectrum in molecules_data:
            f.write(f"# {mol_name}\n")
            f.write(f"{pyname} = [0] * {max_mz}\n")
            for i, val in enumerate(spectrum):
                if val > 0:
                    f.write(f"{pyname}[{i}] = {val:.4f}  # m/z={i+2}\n")
            f.write("\n")
        
        # Write Mass/Charge peaks list
        f.write("# Mass/Charge peaks (m/z values)\n")
        mass_charge_peaks = list(range(2, max_mz + 2))
        f.write(f"mass_charge_peaks = {mass_charge_peaks}\n\n")
        
        # Write NIST_MASS_SPECTRA dictionary
        f.write("# Complete NIST Mass Spectra Database\n")
        f.write("NIST_MASS_SPECTRA = {\n")
        f.write(f"    'Mass/Charge peaks': mass_charge_peaks,\n")
        
        for mol_name, pyname, spectrum in molecules_data:
            f.write(f"    '{mol_name}': {pyname},\n")
        
        f.write("}\n\n")
        
        # Write analysis function
        f.write("def get_molecules_for_mass(target_mass):\n")
        f.write('    """\n')
        f.write("    Get all molecules that have fragments at the specified mass\n")
        f.write("    Args:\n")
        f.write("        target_mass (int): Target m/z value\n")
        f.write("    Returns:\n")
        f.write("        list: List of tuples (molecule_name, intensity)\n")
        f.write('    """\n')
        f.write("    if target_mass not in NIST_MASS_SPECTRA['Mass/Charge peaks']:\n")
        f.write("        return []\n")
        f.write("    \n")
        f.write("    idx = NIST_MASS_SPECTRA['Mass/Charge peaks'].index(target_mass)\n")
        f.write("    molecules_with_fragments = []\n")
        f.write("    \n")
        f.write("    for mol_name, spectrum in NIST_MASS_SPECTRA.items():\n")
        f.write("        if mol_name != 'Mass/Charge peaks':\n")
        f.write("            intensity = spectrum[idx]\n")
        f.write("            if intensity > 0:\n")
        f.write("                molecules_with_fragments.append((mol_name, intensity))\n")
        f.write("    \n")
        f.write("    # Sort by intensity (descending)\n")
        f.write("    molecules_with_fragments.sort(key=lambda x: x[1], reverse=True)\n")
        f.write("    return molecules_with_fragments\n\n")
        
        # Write example usage
        f.write("# Example usage:\n")
        f.write("# molecules_at_28 = get_molecules_for_mass(28)\n")
        f.write("# print(f'Molecules with fragments at m/z=28: {molecules_at_28}')\n")

# Main execution
def main():
    # Get user input for maximum mass
    while True:
        try:
            max_mz_input = input("Enter the maximum m/z value to consider (default: 78): ").strip()
            if not max_mz_input:
                max_mz = 78
            else:
                max_mz = int(max_mz_input)
            if max_mz < 2:
                print("Maximum m/z must be at least 2")
                continue
            break
        except ValueError:
            print("Please enter a valid integer")
    
    # Get output filename
    output_file = input("Enter output filename (default: nist_mass_spectra_database.py): ").strip()
    if not output_file:
        output_file = "nist_mass_spectra_database.py"
    
    # Ensure .py extension
    if not output_file.endswith('.py'):
        output_file += '.py'
    
    print(f"Creating database with m/z range 2-{max_mz}")
    print(f"Output file: {output_file}")
    
    # Create JCAMP directory
    jcamp_dir = "jcamp_files"
    os.makedirs(jcamp_dir, exist_ok=True)
    
    # Get molecule data from NIST
    search_url = "https://webbook.nist.gov/cgi/cbook.cgi?Value=2-100&VType=MW&Formula=&AllowExtra=on&Units=SI&cMS=on"
    print("Fetching molecule list from NIST...")
    ids_and_names = get_molecule_ids_and_names(search_url)
    
    molecules_data = []
    total_molecules = len(ids_and_names)
    
    print(f"Processing {total_molecules} molecules...")
    
    for i, (mol_name, mol_id) in enumerate(ids_and_names, 1):
        print(f"Processing {i}/{total_molecules}: {mol_name}")
        
        jcamp_url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={mol_id}&Index=0&Type=Mass"
        file_path = os.path.join(jcamp_dir, f"{mol_id}.jdx")
        
        resp = requests.get(jcamp_url)
        if "##TITLE=" in resp.text:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(resp.text)
        else:
            print(f"  -> No mass spectrum available for {mol_name}")
            time.sleep(2)
            continue
        
        time.sleep(1)  # Rate limiting
        
        mz_int = parse_jcamp_peak_table(file_path)
        pyname, spectrum = normalize_and_format(mol_name, mz_int, max_mz)
        
        if pyname and spectrum:
            molecules_data.append((mol_name, pyname, spectrum))
            print(f"  -> Added to database")
        else:
            print(f"  -> Could not process spectrum")
    
    # Write the database file
    print(f"\nWriting database to {output_file}...")
    write_mass_spectra_database(output_file, molecules_data, max_mz)
    
    print(f"\nDatabase created successfully!")
    print(f"Total molecules in database: {len(molecules_data)}")
    print(f"Mass range: 2 to {max_mz}")
    print(f"Output file: {output_file}")
    
    # Show example of molecules at a specific mass
    if molecules_data:
        print("\nExample usage:")
        print(f"To find molecules with fragments at m/z=28, run:")
        print(f"  from {output_file[:-3]} import get_molecules_for_mass")
        print(f"  molecules = get_molecules_for_mass(28)")
        print(f"  print(molecules)")

if __name__ == "__main__":
    main()