import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import matplotlib.pyplot as plt


# ================= DATABASE =================

connection = sqlite3.connect("students.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    roll_no TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    cgpa REAL NOT NULL,
    percentage REAL NOT NULL,
    grade TEXT NOT NULL
)
""")

connection.commit()


# ================= MAIN WINDOW =================

root = tk.Tk()
root.title("Student Management System")
root.geometry("1100x750")
root.resizable(True, True)


# ================= FUNCTIONS =================

def calculate_grade(cgpa):
    if cgpa >= 9:
        return "A+"
    elif cgpa >= 8:
        return "A"
    elif cgpa >= 7:
        return "B"
    elif cgpa >= 6:
        return "C"
    elif cgpa >= 5:
        return "D"
    else:
        return "F"


def clear_fields():
    name_entry.delete(0, tk.END)
    roll_entry.delete(0, tk.END)
    branch_entry.delete(0, tk.END)
    cgpa_entry.delete(0, tk.END)
    search_entry.delete(0, tk.END)


# ================= ADD STUDENT =================

def add_student():

    name = name_entry.get().strip()
    roll_no = roll_entry.get().strip()
    branch = branch_entry.get().strip()
    cgpa_text = cgpa_entry.get().strip()

    if not name or not roll_no or not branch or not cgpa_text:
        messagebox.showwarning(
            "Warning",
            "Please fill all fields."
        )
        return

    try:
        cgpa = float(cgpa_text)
    except ValueError:
        messagebox.showerror(
            "Error",
            "CGPA must be a number."
        )
        return

    if cgpa < 0 or cgpa > 10:
        messagebox.showerror(
            "Error",
            "CGPA must be between 0 and 10."
        )
        return

    percentage = cgpa * 10
    grade = calculate_grade(cgpa)

    try:

        cursor.execute("""
        INSERT INTO students
        (name, roll_no, branch, cgpa, percentage, grade)
        VALUES (?, ?, ?, ?, ?, ?)
        """, (
            name,
            roll_no,
            branch,
            cgpa,
            percentage,
            grade
        ))

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Student added successfully!"
        )

        clear_fields()
        view_students()

    except sqlite3.IntegrityError:

        messagebox.showerror(
            "Duplicate Roll Number",
            "This roll number already exists."
        )


# ================= VIEW STUDENTS =================

def view_students():

    for item in student_table.get_children():
        student_table.delete(item)

    cursor.execute("""
    SELECT name, roll_no, branch, cgpa, percentage, grade
    FROM students
    ORDER BY id
    """)

    students = cursor.fetchall()

    for student in students:

        student_table.insert(
            "",
            tk.END,
            values=student
        )


# ================= SEARCH STUDENT =================

def search_student():

    roll_no = search_entry.get().strip()

    if not roll_no:
        messagebox.showwarning(
            "Warning",
            "Enter a roll number to search."
        )
        return

    cursor.execute("""
    SELECT name, roll_no, branch, cgpa, percentage, grade
    FROM students
    WHERE roll_no = ?
    """, (roll_no,))

    student = cursor.fetchone()

    if student:

        name_entry.delete(0, tk.END)
        name_entry.insert(0, student[0])

        roll_entry.delete(0, tk.END)
        roll_entry.insert(0, student[1])

        branch_entry.delete(0, tk.END)
        branch_entry.insert(0, student[2])

        cgpa_entry.delete(0, tk.END)
        cgpa_entry.insert(0, student[3])

        messagebox.showinfo(
            "Student Found",
            f"Name: {student[0]}\n"
            f"Roll Number: {student[1]}\n"
            f"Branch: {student[2]}\n"
            f"CGPA: {student[3]}\n"
            f"Percentage: {student[4]}%\n"
            f"Grade: {student[5]}"
        )

    else:

        messagebox.showerror(
            "Not Found",
            "Student not found."
        )


# ================= UPDATE STUDENT =================

def update_student():

    roll_no = search_entry.get().strip()

    if not roll_no:
        messagebox.showwarning(
            "Warning",
            "Enter the roll number in the search field."
        )
        return

    name = name_entry.get().strip()
    branch = branch_entry.get().strip()
    cgpa_text = cgpa_entry.get().strip()

    if not name or not branch or not cgpa_text:
        messagebox.showwarning(
            "Warning",
            "Please enter Name, Branch and CGPA."
        )
        return

    try:
        cgpa = float(cgpa_text)
    except ValueError:
        messagebox.showerror(
            "Error",
            "CGPA must be a number."
        )
        return

    if cgpa < 0 or cgpa > 10:
        messagebox.showerror(
            "Error",
            "CGPA must be between 0 and 10."
        )
        return

    percentage = cgpa * 10
    grade = calculate_grade(cgpa)

    cursor.execute("""
    UPDATE students
    SET name = ?,
        branch = ?,
        cgpa = ?,
        percentage = ?,
        grade = ?
    WHERE roll_no = ?
    """, (
        name,
        branch,
        cgpa,
        percentage,
        grade,
        roll_no
    ))

    connection.commit()

    if cursor.rowcount > 0:

        messagebox.showinfo(
            "Success",
            "Student updated successfully!"
        )

        clear_fields()
        view_students()

    else:

        messagebox.showerror(
            "Not Found",
            "Student not found."
        )


# ================= DELETE STUDENT =================

def delete_student():

    roll_no = search_entry.get().strip()

    if not roll_no:
        messagebox.showwarning(
            "Warning",
            "Enter the roll number to delete."
        )
        return

    cursor.execute("""
    SELECT name
    FROM students
    WHERE roll_no = ?
    """, (roll_no,))

    student = cursor.fetchone()

    if student is None:

        messagebox.showerror(
            "Not Found",
            "Student not found."
        )
        return

    confirm = messagebox.askyesno(
        "Confirm Delete",
        "Are you sure you want to delete this student?"
    )

    if confirm:

        cursor.execute("""
        DELETE FROM students
        WHERE roll_no = ?
        """, (roll_no,))

        connection.commit()

        messagebox.showinfo(
            "Success",
            "Student deleted successfully!"
        )

        clear_fields()
        view_students()


# ================= PERFORMANCE GRAPH =================

def show_performance_graph():

    cursor.execute("""
    SELECT name, cgpa
    FROM students
    """)

    students = cursor.fetchall()

    if not students:

        messagebox.showinfo(
            "Performance Graph",
            "No student records available."
        )
        return

    names = [student[0] for student in students]
    cgpas = [student[1] for student in students]

    plt.figure(figsize=(10, 5))

    plt.bar(names, cgpas)

    plt.title("Student CGPA Performance")
    plt.xlabel("Students")
    plt.ylabel("CGPA")

    plt.ylim(0, 10)

    plt.xticks(rotation=30)

    plt.tight_layout()

    plt.show()


# ================= EXIT =================

def exit_application():

    connection.close()
    root.destroy()


# ================= TITLE =================

title_label = tk.Label(
    root,
    text="Student Management System",
    font=("Arial", 24, "bold")
)

title_label.pack(pady=15)


# ================= INPUT AREA =================

input_frame = tk.LabelFrame(
    root,
    text="Student Information",
    font=("Arial", 12, "bold"),
    padx=15,
    pady=10
)

input_frame.pack(
    padx=20,
    pady=5
)


# Student Name

tk.Label(
    input_frame,
    text="Student Name:",
    font=("Arial", 11)
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8
)

name_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)

name_entry.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)


# Roll Number

tk.Label(
    input_frame,
    text="Roll Number:",
    font=("Arial", 11)
).grid(
    row=0,
    column=2,
    padx=10,
    pady=8
)

roll_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)

roll_entry.grid(
    row=0,
    column=3,
    padx=10,
    pady=8
)


# Branch

tk.Label(
    input_frame,
    text="Branch:",
    font=("Arial", 11)
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8
)

branch_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)

branch_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)


# CGPA

tk.Label(
    input_frame,
    text="CGPA:",
    font=("Arial", 11)
).grid(
    row=1,
    column=2,
    padx=10,
    pady=8
)

cgpa_entry = tk.Entry(
    input_frame,
    width=28,
    font=("Arial", 11)
)

cgpa_entry.grid(
    row=1,
    column=3,
    padx=10,
    pady=8
)


# ================= SEARCH AREA =================

search_frame = tk.Frame(root)

search_frame.pack(pady=10)

tk.Label(
    search_frame,
    text="Roll Number:",
    font=("Arial", 11)
).pack(
    side="left",
    padx=5
)

search_entry = tk.Entry(
    search_frame,
    width=25,
    font=("Arial", 11)
)

search_entry.pack(
    side="left",
    padx=5
)


# ================= BUTTON AREA =================

button_frame = tk.Frame(root)

button_frame.pack(pady=10)


tk.Button(
    button_frame,
    text="Add Student",
    command=add_student,
    width=16
).grid(row=0, column=0, padx=5, pady=5)


tk.Button(
    button_frame,
    text="View Students",
    command=view_students,
    width=16
).grid(row=0, column=1, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Search Student",
    command=search_student,
    width=16
).grid(row=0, column=2, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Update Student",
    command=update_student,
    width=16
).grid(row=1, column=0, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Delete Student",
    command=delete_student,
    width=16
).grid(row=1, column=1, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Clear",
    command=clear_fields,
    width=16
).grid(row=1, column=2, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Performance Graph",
    command=show_performance_graph,
    width=16
).grid(row=2, column=0, padx=5, pady=5)


tk.Button(
    button_frame,
    text="Exit",
    command=exit_application,
    width=16
).grid(row=2, column=2, padx=5, pady=5)


# ================= TABLE AREA =================

table_frame = tk.LabelFrame(
    root,
    text="Student Records",
    font=("Arial", 12, "bold")
)

table_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


columns = (
    "Name",
    "Roll No",
    "Branch",
    "CGPA",
    "Percentage",
    "Grade"
)


student_table = ttk.Treeview(
    table_frame,
    columns=columns,
    show="headings"
)


# Vertical scrollbar

vertical_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="vertical",
    command=student_table.yview
)

student_table.configure(
    yscrollcommand=vertical_scrollbar.set
)


# Horizontal scrollbar

horizontal_scrollbar = ttk.Scrollbar(
    table_frame,
    orient="horizontal",
    command=student_table.xview
)

student_table.configure(
    xscrollcommand=horizontal_scrollbar.set
)


# Table headings

for column in columns:

    student_table.heading(
        column,
        text=column
    )

    student_table.column(
        column,
        width=160,
        anchor="center"
    )


student_table.grid(
    row=0,
    column=0,
    sticky="nsew"
)

vertical_scrollbar.grid(
    row=0,
    column=1,
    sticky="ns"
)

horizontal_scrollbar.grid(
    row=1,
    column=0,
    sticky="ew"
)


table_frame.grid_rowconfigure(
    0,
    weight=1
)

table_frame.grid_columnconfigure(
    0,
    weight=1
)


# ================= LOAD DATA =================

view_students()


# ================= RUN =================

root.mainloop()