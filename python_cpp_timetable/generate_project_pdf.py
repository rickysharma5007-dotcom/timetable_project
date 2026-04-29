import textwrap
from pathlib import Path


OUTPUT = Path(__file__).with_name("Timetable_Project_Python_Report.pdf")


class SimplePdf:
    def __init__(self):
        self.objects = []
        self.pages = []
        self.width = 595
        self.height = 842
        self.margin = 54

    def add_object(self, data):
        self.objects.append(data)
        return len(self.objects)

    def escape(self, text):
        return text.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    def line(self, x, y, text, size=11, font="F1"):
        return f"BT /{font} {size} Tf {x:.2f} {y:.2f} Td ({self.escape(text)}) Tj ET\n"

    def add_page(self, commands):
        stream = "".join(commands).encode("latin-1", "replace")
        stream_obj = self.add_object(
            f"<< /Length {len(stream)} >>\nstream\n".encode("latin-1")
            + stream
            + b"endstream"
        )
        self.pages.append(stream_obj)

    def build(self, path):
        font_regular = self.add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
        font_bold = self.add_object(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica-Bold >>")

        page_objects = []
        for content_obj in self.pages:
            page_objects.append(
                self.add_object(
                    (
                        f"<< /Type /Page /Parent PAGES_REF 0 R /MediaBox [0 0 {self.width} {self.height}] "
                        f"/Resources << /Font << /F1 {font_regular} 0 R /F2 {font_bold} 0 R >> >> "
                        f"/Contents {content_obj} 0 R >>"
                    ).encode("latin-1")
                )
            )

        kids = " ".join(f"{obj} 0 R" for obj in page_objects)
        pages_obj = self.add_object(f"<< /Type /Pages /Kids [{kids}] /Count {len(page_objects)} >>".encode("latin-1"))
        catalog_obj = self.add_object(f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode("latin-1"))

        patched = []
        for obj in self.objects:
            if isinstance(obj, bytes):
                patched.append(obj.replace(b"PAGES_REF", str(pages_obj).encode("latin-1")))
            else:
                patched.append(obj.replace("PAGES_REF", str(pages_obj)).encode("latin-1"))

        output = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
        offsets = [0]
        for index, obj in enumerate(patched, start=1):
            offsets.append(len(output))
            output.extend(f"{index} 0 obj\n".encode("latin-1"))
            output.extend(obj)
            output.extend(b"\nendobj\n")

        xref_offset = len(output)
        output.extend(f"xref\n0 {len(patched) + 1}\n".encode("latin-1"))
        output.extend(b"0000000000 65535 f \n")
        for offset in offsets[1:]:
            output.extend(f"{offset:010d} 00000 n \n".encode("latin-1"))
        output.extend(
            (
                f"trailer\n<< /Size {len(patched) + 1} /Root {catalog_obj} 0 R >>\n"
                f"startxref\n{xref_offset}\n%%EOF\n"
            ).encode("latin-1")
        )
        path.write_bytes(output)


class ReportWriter:
    def __init__(self):
        self.pdf = SimplePdf()
        self.commands = []
        self.y = 780
        self.page_no = 0

    def new_page(self):
        if self.commands:
            self.footer()
            self.pdf.add_page(self.commands)
        self.page_no += 1
        self.commands = []
        self.y = 780

    def footer(self):
        self.commands.append(self.pdf.line(54, 32, f"Timetable Generator Project Report | Page {self.page_no}", 8))

    def ensure_space(self, needed):
        if self.y - needed < 70:
            self.new_page()

    def text(self, text, size=11, bold=False, indent=0, width=88, gap=15):
        font = "F2" if bold else "F1"
        lines = textwrap.wrap(text, width=width - indent) or [""]
        self.ensure_space(len(lines) * gap + 4)
        for line in lines:
            self.commands.append(self.pdf.line(54 + indent * 4.5, self.y, line, size=size, font=font))
            self.y -= gap
        self.y -= 2

    def heading(self, text):
        self.ensure_space(34)
        self.y -= 8
        self.commands.append(self.pdf.line(54, self.y, text, size=15, font="F2"))
        self.y -= 22

    def bullet(self, text):
        self.text("- " + text, size=10.5, indent=2, width=86, gap=14)

    def title_page(self):
        self.new_page()
        self.commands.append(self.pdf.line(54, 770, "Timetable Generator Project Report", size=24, font="F2"))
        self.commands.append(self.pdf.line(54, 735, "Python Frontend and C++ DSA Backend", size=16, font="F1"))
        self.y = 690
        self.text(
            "This report explains the timetable generator project in a simple presentation-friendly way. "
            "It covers both sides of the project: the Python GUI layer and the C++ backend layer. "
            "Python handles the application interface, while the backend handles the core data structures "
            "and timetable generation logic.",
            size=12,
            width=82,
            gap=17,
        )
        self.text("Project files referred to: gui.py, main.cpp, scheduler.cpp, trie.cpp, professors.json, and timetable.json.", size=11, width=82)

    def build_report(self):
        self.title_page()

        self.heading("Project Overview")
        self.text(
            "The project is an institute timetable generator. It allows the user to manage professor names, "
            "generate timetables for multiple sections, view each section, find the next class, and export a "
            "readable timetable file."
        )
        self.text(
            "The project has two layers. Python is the main application layer and provides the complete GUI. "
            "The C++ layer is used as the DSA backend for Trie operations and priority-queue based timetable generation."
        )

        self.heading("My Main Work in Python")
        self.bullet("Built the GUI in Python using Tkinter, including the professor panel, timetable display, buttons, input boxes, dropdowns, status messages, and result list.")
        self.bullet("Connected Python to the compiled C++ backend using subprocess so the GUI can run commands like trie insert, trie search, trie all, and schedule.")
        self.bullet("Used Python json handling to read backend responses and convert them into data that can be shown in the GUI.")
        self.bullet("Added validation for section count so wrong input does not break timetable generation.")
        self.bullet("Stored the latest timetable in Python so it can be reused for section switching, next-class checking, and export.")
        self.bullet("Implemented the next-class feature using Python datetime logic and the current system time.")
        self.bullet("Implemented timetable export from Python into a readable text file.")

        self.heading("Why Python Is Important Here")
        self.text(
            "Python makes the project user-friendly. Without the Python file, the project would only run as command-line commands. "
            "The Python GUI turns the DSA backend into a proper application where a user can click buttons, enter data, view tables, and understand the output."
        )
        self.text(
            "Python also acts as the controller of the project. It decides when to call the backend, checks inputs, parses JSON output, updates the screen, "
            "and keeps the latest timetable available for extra features."
        )

        self.heading("Backend Work")
        self.text(
            "The backend is written in C++ and works like the logic engine of the project. Python sends commands to it, "
            "and the backend performs the data-structure operations, generates timetable data, saves files, and returns JSON output."
        )
        self.bullet("main.cpp handles command routing. It receives commands such as trie insert, trie search, trie all, trie prefix, and schedule.")
        self.bullet("trie.cpp and trie.h implement professor management using a Trie.")
        self.bullet("scheduler.cpp and scheduler.h implement timetable generation using a Priority Queue.")
        self.bullet("professors.json stores saved professor names so the data remains available between runs.")
        self.bullet("timetable.json stores the generated timetable in a structured format.")
        self.bullet("The backend prints JSON to stdout, and Python reads that output using subprocess.")

        self.heading("Backend Modules")
        self.bullet("main.cpp: entry point of the backend. It checks the command-line arguments and calls the correct module.")
        self.bullet("Trie module: inserts professor names, searches exact names, returns all saved professors, and supports prefix-based search.")
        self.bullet("Scheduler module: creates days, slots, subjects, sections, and final timetable cells.")
        self.bullet("JSON helpers: convert backend results into JSON text so Python can parse them easily.")

        self.heading("Trie Backend Explanation")
        self.text(
            "The Trie is used for professor management. Each professor name is normalized by trimming spaces and converting it to lowercase. "
            "Then every character is stored level by level in the Trie. This makes searching efficient because the program follows one character path "
            "instead of comparing the input with every full name manually."
        )
        self.bullet("TrieNode stores a map from character to child node.")
        self.bullet("isEnd marks the end of a complete professor name.")
        self.bullet("insertProfessor creates missing character nodes and marks the last node as the end.")
        self.bullet("searchProfessor follows the character path and returns true only if the full name exists.")
        self.bullet("prefixSearch reaches the prefix node and then collects all matching names below it.")

        self.heading("Scheduler Backend Explanation")
        self.text(
            "The scheduler creates a weekly timetable for each section. It has five working days and six slots per day, so each section has "
            "30 timetable cells. Subjects are added to a max heap priority queue based on their credits. A subject with more credits has more "
            "lectures and gets scheduled earlier."
        )
        self.bullet("Each Subject stores name, credits, and teacher.")
        self.bullet("Each Cell stores subject and teacher for one timetable slot.")
        self.bullet("Each SectionTimetable stores the section name and its list of 30 cells.")
        self.bullet("The priority queue stores remaining lectures and subject index.")
        self.bullet("After one lecture is placed, the remaining count is reduced and pushed back if more lectures are left.")
        self.bullet("teacherBusy is a set that stores teacher_day_slot keys to avoid assigning the same teacher to two sections at the same time.")

        self.heading("Backend Flow")
        self.bullet("Python runs main.exe with arguments.")
        self.bullet("main.cpp reads the first argument and decides whether to run Trie logic or scheduling logic.")
        self.bullet("For Trie commands, saved professor names are loaded from professors.json and inserted into a Trie.")
        self.bullet("For schedule commands, the scheduler creates timetables for the requested number of sections.")
        self.bullet("The backend converts the result into JSON and prints it.")
        self.bullet("Python captures the JSON output, parses it, and displays it in the GUI.")

        self.heading("Python Concepts Used")
        self.bullet("Tkinter classes and widgets: Tk, Frame, Label, Button, Entry, Listbox, OptionMenu, and messagebox.")
        self.bullet("Functions and classes: the TimetableApp class organizes the GUI and separates features into methods.")
        self.bullet("File paths: os.path is used to locate main.exe, timetable.json, and timetable.txt inside the project folder.")
        self.bullet("Subprocess: Python runs the C++ executable and captures its JSON output.")
        self.bullet("JSON parsing: Python converts backend JSON text into dictionaries and lists.")
        self.bullet("Date and time: datetime.now() is used to find the upcoming class.")
        self.bullet("Exception handling: try/except blocks show user-friendly errors instead of crashing the GUI.")

        self.heading("Data Structures Used")
        self.bullet("Trie: used for professor management. Each character of a professor name is stored in a tree-like structure. It supports insertion, exact search, and prefix search.")
        self.bullet("Priority Queue / Max Heap: used in timetable generation. Subjects with more remaining lectures get higher priority and are scheduled first.")
        self.bullet("Vector / List: used to store days, slots, subjects, timetable cells, professor names, and section timetables.")
        self.bullet("Map: used inside each Trie node to map a character to the next child node.")
        self.bullet("Set: used by the scheduler to track teacher-day-slot combinations and avoid teacher clashes across sections.")
        self.bullet("Dictionary / JSON object: used when Python receives timetable data with days, slots, and sections.")
        self.bullet("2D timetable represented as a flat list: each section has 30 cells for 5 days x 6 slots.")

        self.heading("How the Project Works")
        self.bullet("The user opens the GUI by running python gui.py.")
        self.bullet("For professor operations, Python sends commands to the C++ executable and displays the JSON response.")
        self.bullet("For timetable generation, Python sends the number of sections to the scheduler.")
        self.bullet("The scheduler uses a priority queue to place subjects into free slots while checking teacher conflicts.")
        self.bullet("The backend returns JSON. Python reads it, stores it, and draws the selected section as a timetable grid.")
        self.bullet("The user can switch sections, check the next class, and export the timetable.")

        self.heading("Example Explanation for Viva")
        self.text(
            "My work includes both Python and backend integration. In Python, I created the Tkinter GUI, handled user input, connected the GUI "
            "with the backend using subprocess, parsed JSON output, displayed the timetable, and added features like next class and export. "
            "In the backend, the project demonstrates Trie for professor search and Priority Queue for scheduling subjects based on credits. "
            "The backend also checks teacher conflicts and returns structured JSON to the Python GUI."
        )

        self.heading("Conclusion")
        self.text(
            "This project combines Python application development with important data structures. Python makes the project interactive and easy to use, "
            "while Trie and Priority Queue show the DSA logic behind professor management and timetable generation."
        )

        self.footer()
        self.pdf.add_page(self.commands)
        self.pdf.build(OUTPUT)


if __name__ == "__main__":
    writer = ReportWriter()
    writer.build_report()
    print(OUTPUT)
