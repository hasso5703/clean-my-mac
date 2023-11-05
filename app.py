import os
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import asyncio

def find_large_files(path, min_size, excluded_folders):
    large_files = []
    for foldername, subfolders, filenames in os.walk(path):
        folder_name = os.path.basename(foldername)
        if folder_name in excluded_folders:
            continue
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            if os.path.exists(filepath) and not os.path.islink(filepath):
                filesize = os.path.getsize(filepath)
                if filesize >= min_size:
                    large_files.append((filename, filesize, filepath))
    return large_files

async def list_large_files():
    directory = entry_path.get()
    min_size = int(entry_min_size.get()) * 1024 * 1024
    for item in tree.get_children():
        tree.delete(item)
    
    num_folders_to_analyze = sum(1 for root, dirs, files in os.walk(directory))
    progress["maximum"] = num_folders_to_analyze
    progress["value"] = 0

    async def analyze_folders(root):
        large_files = find_large_files(root, min_size, excluded_folders)
        for file_info in large_files:
            filename, filesize, filepath = file_info
            tree.insert('', 'end', values=(filename, f"{filesize / (1024 * 1024):.2f} Mo", filepath))
            progress["value"] += 1
            await asyncio.sleep(0)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, lambda: None)  # Ensure an event loop is running

    for root, dirs, files in os.walk(directory):
        await analyze_folders(root)

def open_file_location():
    selected_item = tree.selection()
    if selected_item:
        filepath = tree.item(selected_item, "values")[2]
        file_directory = os.path.dirname(filepath)
        os.system(f'open "{file_directory}"')

async def main():
    window = tk.Tk()
    window.title("Liste des fichiers de plus de 100 Mo")

    progress = ttk.Progressbar(window, mode="determinate")
    progress.grid(row=4, column=0, columnspan=3, pady=10)

    window.geometry("800x400")

    label_path = ttk.Label(window, text="Chemin du répertoire:")
    label_path.grid(row=0, column=0)

    default_directory = "/Users/hasan"
    entry_path = ttk.Entry(window)
    entry_path.insert(0, default_directory)
    entry_path.grid(row=0, column=1, sticky="ew")

    label_min_size = ttk.Label(window, text="Taille minimale (Mo):")
    label_min_size.grid(row=1, column=0)
    entry_min_size = ttk.Entry(window)
    entry_min_size.insert(0, "100")
    entry_min_size.grid(row=1, column=1, sticky="ew")

    search_button = ttk.Button(window, text="Rechercher", command=lambda: asyncio.create_task(list_large_files()))
    search_button.grid(row=2, columnspan=2)

    tree = ttk.Treeview(window, columns=("Nom du fichier", "Taille (Mo)", "Chemin complet"), show="headings")
    tree.heading("Nom du fichier", text="Nom du fichier")
    tree.heading("Taille (Mo)", text="Taille (Mo)")
    tree.heading("Chemin complet", text="Chemin complet")
    tree.column("Nom du fichier", width=200)
    tree.column("Taille (Mo)", width=100)
    tree.grid(row=3, column=0, columnspan=3, sticky="nsew")

    scrollbar_x = ttk.Scrollbar(window, orient="horizontal", command=tree.xview)
    scrollbar_x.grid(row=5, column=0, columnspan=3, sticky="ew")
    tree.configure(xscrollcommand=scrollbar_x.set)

    open_button = ttk.Button(window, text="Ouvrir le dossier", command=open_file_location)
    open_button.grid(row=5, columnspan=2)

    window.columnconfigure(1, weight=1)
    window.rowconfigure(3, weight=1)

    excluded_folders = [".git", "node_modules"]

    window.mainloop()

if __name__ == "__main__":
    asyncio.run(main())
