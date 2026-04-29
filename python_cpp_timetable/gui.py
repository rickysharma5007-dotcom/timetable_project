import json
import os
import subprocess
import tkinter as tk
from tkinter import messagebox, scrolledtext

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
EXE_NAME = "main.exe" if os.name == "nt" else "main"
EXE_PATH = os.path.join(PROJECT_DIR, EXE_NAME)
root = None
frame = None

def run_cpp(args):
    if not os.path.exists(EXE_PATH):
        raise FileNotFoundError("Compile main.exe first.")
    result = subprocess.run([EXE_PATH] + args, cwd=PROJECT_DIR, capture_output=True, text=True)
    return json.loads(result.stdout)

def clear():
    global frame
    if frame:
        frame.destroy()
    frame = tk.Frame(root, bg="#f5f5f5", padx=20, pady=20)
    frame.pack(fill="both", expand=True)

def button(text, command):
    return tk.Button(frame, text=text, command=command, width=24, bg="#4a90e2", fg="white", font=("Arial", 12, "bold"), pady=7)

def menu():
    clear()
    tk.Label(frame, text="Timetable Generator", bg="#f5f5f5", font=("Arial", 24, "bold")).pack(pady=50)
    button("Manage Professors", professors_page).pack(pady=15)
    button("Generate Timetable", timetable_page).pack(pady=15)
    tk.Label(frame, text="Python GUI + C++ Backend", bg="#f5f5f5", fg="#555").pack(side="bottom")

def professors_page():
    clear()
    tk.Label(frame, text="Professor Management", bg="#f5f5f5", font=("Arial", 20, "bold")).pack(pady=10)
    entry = tk.Entry(frame, width=35, font=("Arial", 12))
    entry.pack(pady=8)
    status = tk.Label(frame, text="", bg="#f5f5f5", font=("Arial", 11))
    status.pack()
    names = tk.Listbox(frame, width=45, height=12, font=("Arial", 11))
    names.pack(pady=10, fill="both", expand=True)

    def show_all():
        try:
            data = run_cpp(["trie", "all"])
            names.delete(0, tk.END)
            for name in data.get("professors", []):
                names.insert(tk.END, name)
            status.config(text="All professors loaded.", fg="blue")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def add():
        try:
            data = run_cpp(["trie", "insert", entry.get().strip()])
            status.config(text=data.get("message", ""), fg="green")
            entry.delete(0, tk.END)
            show_all()
        except Exception as error:
            messagebox.showerror("Error", str(error))

    def search():
        try:
            data = run_cpp(["trie", "search", entry.get().strip()])
            color = "green" if data.get("success") else "red"
            status.config(text=data.get("message", ""), fg=color)
        except Exception as error:
            messagebox.showerror("Error", str(error))

    button("Add Professor", add).pack(pady=4)
    button("Search Professor", search).pack(pady=4)
    button("Show All", show_all).pack(pady=4)
    button("Back", menu).pack(pady=12)
    show_all()

def timetable_page():
    clear()
    tk.Label(frame, text="Generate Timetable", bg="#f5f5f5", font=("Arial", 20, "bold")).pack(pady=8)
    section_entry = tk.Entry(frame, width=10, font=("Arial", 12))
    section_entry.insert(0, "5")
    section_entry.pack(pady=8)
    output = scrolledtext.ScrolledText(frame, width=90, height=23, font=("Consolas", 10))
    output.pack(fill="both", expand=True, pady=8)

    def generate():
        try:
            data = run_cpp(["schedule", section_entry.get().strip()])
            output.delete("1.0", tk.END)
            for section, cells in data["sections"].items():
                output.insert(tk.END, section + "\n" + "-" * 40 + "\n")
                for day_index, day in enumerate(data["days"]):
                    output.insert(tk.END, day + "\n")
                    for slot_index, slot in enumerate(data["slots"]):
                        subject, teacher = cells[day_index * len(data["slots"]) + slot_index]
                        text = slot + ": " + subject + ("" if teacher == "" else " - " + teacher)
                        output.insert(tk.END, "  " + text + "\n")
                    output.insert(tk.END, "\n")
                output.insert(tk.END, "\n")
        except Exception as error:
            messagebox.showerror("Error", str(error))

    button("Generate", generate).pack(pady=4)
    button("Back", menu).pack(pady=4)

root = tk.Tk()
root.title("Timetable Generator"); root.geometry("900x650"); root.configure(bg="#f5f5f5")
menu()
root.mainloop()
