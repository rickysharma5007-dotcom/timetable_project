# Timetable Generator using Trie and Priority Queue

This is a 2nd-year Data Structures & Algorithms project with:

- Python Tkinter GUI for user interaction.
- C++ core for Trie and Priority Queue logic.
- JSON files for communication and storage.
- No database and no networking.
- Presentation features like next class, export, regenerate, section dropdown, and status messages.

## File Structure

```text
project/
  main.cpp
  trie.cpp
  trie.h
  scheduler.cpp
  scheduler.h
  gui.py
  timetable.json
  professors.json
```

## Compile C++ Backend

```bash
g++ main.cpp trie.cpp scheduler.cpp -o main.exe
```

On Linux/macOS:

```bash
g++ main.cpp trie.cpp scheduler.cpp -o main
```

## Run GUI

```bash
python gui.py
```

## CLI Examples

```bash
./main.exe trie insert "John"
./main.exe trie search "John"
./main.exe trie all
./main.exe trie prefix "Jo"
./main.exe schedule 5
```

## HOW TO EXPLAIN PROJECT

Sir, this project demonstrates use of Trie and Priority Queue in a timetable generation system.

Trie is used for professor management. It provides fast search because names are stored character by character. It also supports prefix-based lookup, so names starting with the same letters can be found efficiently.

The scheduler uses a max heap Priority Queue. Subjects with higher credits need more lectures, so they are given higher priority and scheduled first. This is better than a naive greedy approach because important high-credit subjects are less likely to be left without enough slots.

Architecture:

- Python handles only the GUI using Tkinter.
- C++ handles all data structures and timetable logic.
- `trie.cpp` handles Trie.
- `scheduler.cpp` handles Priority Queue and final timetable placement.
- Python calls the C++ executable using subprocess.
- C++ returns JSON and also saves `timetable.json`.

Demo Flow:

1. Open the GUI using `python gui.py`.
2. Click Manage Professors.
3. Add a professor name.
4. Search the same professor name.
5. Go back and click Generate Timetable.
6. Enter number of sections and generate the timetable.
7. Use the section dropdown to switch between SectionA, SectionB, and other sections.
8. Click Show Next Class to find the next upcoming class using current system time.
9. Click Export Timetable to save a readable `timetable.txt` file.
10. Click Generate Again to re-run the C++ scheduler.

Key C++ lines:

- `trie.insertProfessor(name)` inserts professor names into the Trie.
- `trie.searchProfessor(name)` performs exact search.
- `std::priority_queue` creates the max heap.
- `pq.push(...)` inserts subjects based on remaining lectures.
- `pq.pop()` selects the subject with highest priority.
- `teacherBusy` prevents teacher conflicts across sections.
- `main.exe trie all` returns all stored professor names for the GUI list.
