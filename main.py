from tkinter import Tk, filedialog
from yadg.extractors.quadstar.sac import extract_from_path
from pathlib import Path

# Hide the main Tk window
root = Tk()
root.withdraw()

file_path = filedialog.askopenfilename(
    title="Select a .sac file",
    filetypes=[("SAC files", "*.sac")]
)

if file_path:
    datatree = extract_from_path(Path(file_path))
else:
    print("No file selected.")
    exit()

# Print the structure of the DataTree to understand how cycles are stored
print("datatree:", datatree)
print("Children nodes:", datatree.children)
print("Attributes:", getattr(datatree, "attrs", None))
print("Keys:", list(datatree.keys()) if hasattr(datatree, "keys") else None)

# If datatree has children nodes (e.g., one per cycle), list them
if hasattr(datatree, "children"):
    print("Cycle node names:", list(datatree.children.keys()))