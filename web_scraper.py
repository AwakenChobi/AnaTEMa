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

def normalize_and_format(mol_name, mz_int, max_mz=50):
    if not mz_int:
        return ""
    max_int = max(i for _, i in mz_int)
    arr = [0.0] * max_mz
    for mz, inten in mz_int:
        idx = mz - 2  # m/z=2 corresponde a idx=0
        if 0 <= idx < max_mz:
            arr[idx] = inten / max_int
    pyname = re.sub(r'\W|^(?=\d)', '_', mol_name.lower())
    lines = [f"{pyname} = [0] * {max_mz}"]
    for i, val in enumerate(arr):
        if val > 0:
            lines.append(f"{pyname}[{i}] = {val:.4f}  # m/z={i+2}")
    return "\n".join(lines)

# Crear carpeta para los archivos JCAMP si no existe
jcamp_dir = "jcamp_files"
os.makedirs(jcamp_dir, exist_ok=True)

search_url = "https://webbook.nist.gov/cgi/cbook.cgi?Value=2-51&VType=MW&Formula=&AllowExtra=on&Units=SI&cMS=on"
ids_and_names = get_molecule_ids_and_names(search_url)

for mol_name, mol_id in ids_and_names:
    jcamp_url = f"https://webbook.nist.gov/cgi/cbook.cgi?JCAMP={mol_id}&Index=0&Type=Mass"
    file_path = os.path.join(jcamp_dir, f"{mol_id}.jdx")
    resp = requests.get(jcamp_url)
    if "##TITLE=" in resp.text:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(resp.text)
    else:
        print(f"# {mol_name} (sin espectro de masas JCAMP)")
        print()
        time.sleep(2)
        continue
    time.sleep(5)  # Espera 5 segundos entre descargas

    mz_int = parse_jcamp_peak_table(file_path)
    print(f"# {mol_name}")
    print(normalize_and_format(mol_name, mz_int))
    print()