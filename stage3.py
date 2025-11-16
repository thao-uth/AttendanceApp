import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import sqlite3
from datetime import datetime
import os

DB_FILE = "attendance_gui.db"
LOGO_FILE = "uth.png"

# =================== DATABASE SETUP ===================
def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # Bảng người dùng
    c.execute("""
    CREATE TABLE IF NOT EXISTS users (
        username TEXT PRIMARY KEY,
        password TEXT,
        role TEXT
    )
    """)

    # Bảng điểm danh
    c.execute("""
    CREATE TABLE IF NOT EXISTS attendance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id TEXT,
        student_name TEXT,
        date TEXT,
        status TEXT
    )
    """)

    # Bảng môn học (Course)
    c.execute("""
    CREATE TABLE IF NOT EXISTS courses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        course_code TEXT,
        course_name TEXT
    )
    """)

    # Bảng lớp (Class)
    c.execute("""
    CREATE TABLE IF NOT EXISTS classes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_code TEXT,
        class_name TEXT,
        course_id INTEGER
    )
    """)

    # Tài khoản mặc định
    c.execute("INSERT OR IGNORE INTO users VALUES ('admin','admin','admin')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('teacher','1234','teacher')")
    c.execute("INSERT OR IGNORE INTO users VALUES ('student','0000','student')")

    conn.commit()
    conn.close()


init_db()


# =================== MAIN APPLICATION ===================
class AttendanceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Attendance System")
        self.root.geometry("950x600")
        self.root.resizable(False, False)
        self.logo_path = LOGO_FILE

        self.current_user = None
        self.current_role = None

        self.create_login_screen()

    # ---------- HEADER ----------
    def create_header(self):
        header = tk.Frame(self.root, bg="#d9e1f2", height=70)
        header.pack(fill="x")

        # Logo UTH
        try:
            if os.path.exists(self.logo_path):
                img = Image.open(self.logo_path)
                img = img.resize((150, 90), Image.LANCZOS)
                self.logo = ImageTk.PhotoImage(img)
                tk.Label(header, image=self.logo, bg="#d9e1f2").pack(
                    side="right", padx=30, pady=2
                )
        except Exception:
            pass

        tk.Label(
            header,
            text="Student Attendance System",
            font=("Times New Roman", 22, "bold"),
            fg="navy",
            bg="#d9e1f2",
        ).pack(side="left", padx=60, pady=5)

    # ---------- LOGIN SCREEN ----------
    def create_login_screen(self):
        for w in self.root.winfo_children():
            w.destroy()

        self.root.configure(bg="#f2f4f7")
        self.create_header()

        login_frame = tk.Frame(self.root, bg="#f2f4f7")
        login_frame.place(relx=0.5, rely=0.55, anchor="center")

        tk.Label(
            login_frame,
            text="User Login",
            font=("Times New Roman", 20, "bold"),
            fg="#003366",
            bg="#f2f4f7",
        ).grid(row=0, column=0, columnspan=2, pady=(20, 10))

        tk.Label(
            login_frame,
            text="Username:",
            font=("Times New Roman", 14),
            bg="#f2f4f7",
        ).grid(row=1, column=0, padx=15, pady=10, sticky="e")
        self.username_entry = tk.Entry(
            login_frame, font=("Times New Roman", 14), width=25, bd=2, relief="solid"
        )
        self.username_entry.grid(row=1, column=1, padx=15, pady=10)

        tk.Label(
            login_frame,
            text="Password:",
            font=("Times New Roman", 14),
            bg="#f2f4f7",
        ).grid(row=2, column=0, padx=15, pady=10, sticky="e")
        self.password_entry = tk.Entry(
            login_frame,
            font=("Times New Roman", 14),
            show="*",
            width=25,
            bd=2,
            relief="solid",
        )
        self.password_entry.grid(row=2, column=1, padx=15, pady=10)

        tk.Button(
            login_frame,
            text="Login",
            font=("Times New Roman", 14, "bold"),
            bg="#2e8b57",
            fg="white",
            activebackground="#2f975e",
            width=15,
            height=1,
            relief="flat",
            command=self.login,
        ).grid(row=3, column=0, columnspan=2, pady=(15, 5))

        tk.Button(
            login_frame,
            text="Reset Password",
            font=("Times New Roman", 12, "underline"),
            bg="#f2f4f7",
            fg="#003366",
            bd=0,
            cursor="hand2",
            command=self.open_reset_password_window,
        ).grid(row=4, column=0, columnspan=2, pady=(0, 10))

        self.current_user = None
        self.current_role = None

    # ---------- LOGIN LOGIC ----------
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showwarning("Input Error", "Please enter username and password.")
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "SELECT role FROM users WHERE username=? AND password=?",
            (username, password),
        )
        result = c.fetchone()
        conn.close()

        if not result:
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        role = result[0]
        self.current_user = username
        self.current_role = role

        messagebox.showinfo("Welcome", f"Welcome {username} ({role})")

        if role == "teacher":
            self.create_teacher_screen()
        elif role == "student":
            self.create_student_screen()
        elif role == "admin":
            self.create_admin_screen()
        else:
            messagebox.showerror("Role Error", "Unknown user role!")

    # ---------- TEACHER SCREEN ----------
    def create_teacher_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg="white")
        self.create_header()

        tk.Label(
            self.root,
            text="Teacher Dashboard",
            font=("Times New Roman", 20, "bold"),
            fg="navy",
            bg="white",
        ).pack(pady=15)

        self.create_attendance_form()
        self.create_table_buttons(role="teacher")
        self.load_attendance()

    # ---------- STUDENT SCREEN ----------
    def create_student_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg="white")
        self.create_header()

        tk.Label(
            self.root,
            text="Student Dashboard",
            font=("Times New Roman", 20, "bold"),
            fg="darkred",
            bg="white",
        ).pack(pady=10)

        self.create_attendance_form()
        self.create_table_buttons(role="student")
        self.load_attendance()

    # ---------- ADMIN SCREEN ----------
    def create_admin_screen(self):
        for w in self.root.winfo_children():
            w.destroy()
        self.root.configure(bg="white")
        self.create_header()

        tk.Label(
            self.root,
            text="Admin Dashboard",
            font=("Times New Roman", 20, "bold"),
            fg="darkgreen",
            bg="white",
        ).pack(pady=10)

        # Notebook tabs: Accounts, Courses, Classes
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill="both", expand=True, padx=15, pady=10)

        # Tabs
        self.tab_accounts = tk.Frame(notebook, bg="white")
        self.tab_courses = tk.Frame(notebook, bg="white")
        self.tab_classes = tk.Frame(notebook, bg="white")

        notebook.add(self.tab_accounts, text="Manage Accounts")
        notebook.add(self.tab_courses, text="Manage Courses")
        notebook.add(self.tab_classes, text="Manage Classes")

        self.build_accounts_tab()
        self.build_courses_tab()
        self.build_classes_tab()

        # Nút logout
        tk.Button(
            self.root,
            text="Logout",
            command=self.create_login_screen,
            bg="red",
            fg="white",
            font=("Times New Roman", 13),
            width=12,
        ).pack(pady=5)

    # ---------- ATTENDANCE FORM ----------
    def create_attendance_form(self):
        form_frame = tk.Frame(self.root, bg="white")
        form_frame.pack(pady=15)

        tk.Label(
            form_frame,
            text="Student ID:",
            font=("Times New Roman", 14),
            bg="white",
        ).grid(row=0, column=0, padx=8, pady=5, sticky="e")
        self.student_id = tk.Entry(form_frame, font=("Times New Roman", 14), width=14)
        self.student_id.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(
            form_frame,
            text="Student Name:",
            font=("Times New Roman", 14),
            bg="white",
        ).grid(row=0, column=2, padx=8, pady=5, sticky="e")
        self.student_name = tk.Entry(
            form_frame, font=("Times New Roman", 14), width=18
        )
        self.student_name.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(
            form_frame,
            text="Status:",
            font=("Times New Roman", 14),
            bg="white",
        ).grid(row=0, column=4, padx=8, pady=5, sticky="e")
        self.status_var = tk.StringVar()
        combo = ttk.Combobox(
            form_frame,
            textvariable=self.status_var,
            values=["Present", "Absent", "Late"],
            width=12,
            font=("Times New Roman", 13),
        )
        combo.grid(row=0, column=5, padx=5, pady=5)
        combo.current(0)

        tk.Button(
            form_frame,
            text="Save Attendance",
            font=("Times New Roman", 13, "bold"),
            bg="green",
            fg="white",
            width=16,
            command=self.save_attendance,
        ).grid(row=0, column=6, padx=10, pady=5)

        cols = ("id", "student_id", "student_name", "date", "status")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings", height=12)
        for c in cols:
            self.tree.heading(c, text=c.capitalize())
            self.tree.column(c, width=150, anchor="center")
        self.tree.pack(pady=10, fill="x", padx=20)

    # ---------- BUTTONS UNDER TABLE ----------
    def create_table_buttons(self, role="teacher"):
        btn_frame = tk.Frame(self.root, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Refresh",
            command=self.load_attendance,
            bg="blue",
            fg="white",
            font=("Times New Roman", 13),
            width=10,
        ).pack(side="left", padx=10)

        if role == "teacher":
            tk.Button(
                btn_frame,
                text="Reset All",
                command=self.reset_attendance,
                bg="orange",
                fg="black",
                font=("Times New Roman", 13),
                width=12,
            ).pack(side="left", padx=10)

            tk.Button(
                btn_frame,
                text="History",
                command=self.open_history_window,
                bg="#6c757d",
                fg="white",
                font=("Times New Roman", 13),
                width=10,
            ).pack(side="left", padx=10)

            tk.Button(
                btn_frame,
                text="Report",
                command=self.open_report_window,
                bg="#17a2b8",
                fg="white",
                font=("Times New Roman", 13),
                width=10,
            ).pack(side="left", padx=10)

        elif role == "student":
            tk.Button(
                btn_frame,
                text="My History",
                command=self.open_history_window,
                bg="#6c757d",
                fg="white",
                font=("Times New Roman", 13),
                width=12,
            ).pack(side="left", padx=10)

        # Update profile dùng chung cho teacher & student
        tk.Button(
            btn_frame,
            text="Update Profile",
            command=self.open_update_profile_window,
            bg="#555555",
            fg="white",
            font=("Times New Roman", 13),
            width=14,
        ).pack(side="left", padx=10)

        tk.Button(
            btn_frame,
            text="Logout",
            command=self.create_login_screen,
            bg="red",
            fg="white",
            font=("Times New Roman", 13),
            width=12,
        ).pack(side="left", padx=10)

    # ---------- SAVE ATTENDANCE ----------
    def save_attendance(self):
        sid = self.student_id.get().strip()
        name = self.student_name.get().strip()
        status = self.status_var.get().strip()

        if not sid or not name:
            messagebox.showwarning(
                "Input Error", "Please enter both Student ID and Name."
            )
            return

        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "INSERT INTO attendance (student_id, student_name, date, status) "
                "VALUES (?, ?, ?, ?)",
                (sid, name, datetime.now().strftime("%Y-%m-%d %H:%M"), status),
            )
            conn.commit()
            conn.close()

            messagebox.showinfo("Success", "Attendance saved successfully.")
            self.student_id.delete(0, tk.END)
            self.student_name.delete(0, tk.END)
            self.load_attendance()
        except Exception as e:
            messagebox.showerror("DB Error", f"Error saving attendance:\n{e}")

    # ---------- LOAD ATTENDANCE ----------
    def load_attendance(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT * FROM attendance ORDER BY id DESC")
            rows = c.fetchall()
            conn.close()
            for r in rows:
                self.tree.insert("", tk.END, values=r)
        except Exception as e:
            messagebox.showerror("DB Error", f"Load error:\n{e}")

    # ---------- RESET ----------
    def reset_attendance(self):
        if not messagebox.askyesno("Confirm", "Delete all attendance records?"):
            return
        try:
            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("DELETE FROM attendance")
            conn.commit()
            conn.close()
            self.load_attendance()
            messagebox.showinfo("Reset", "All records cleared.")
        except Exception as e:
            messagebox.showerror("DB Error", f"Reset error:\n{e}")

    # ====================================================
    #           RESET PASSWORD (FORGOT)
    # ====================================================
    def open_reset_password_window(self):
        win = tk.Toplevel(self.root)
        win.title("Reset Password")
        win.geometry("350x220")
        win.resizable(False, False)

        tk.Label(
            win, text="Reset Password", font=("Times New Roman", 16, "bold")
        ).pack(pady=10)

        form = tk.Frame(win)
        form.pack(pady=5, padx=10)

        tk.Label(form, text="Username:", font=("Times New Roman", 12)).grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        username_entry = tk.Entry(form, font=("Times New Roman", 12), width=22)
        username_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="New Password:", font=("Times New Roman", 12)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        new_pass_entry = tk.Entry(
            form, font=("Times New Roman", 12), width=22, show="*"
        )
        new_pass_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Confirm Password:", font=("Times New Roman", 12)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        confirm_entry = tk.Entry(
            form, font=("Times New Roman", 12), width=22, show="*"
        )
        confirm_entry.grid(row=2, column=1, padx=5, pady=5)

        def do_reset():
            username = username_entry.get().strip()
            new_pw = new_pass_entry.get().strip()
            confirm_pw = confirm_entry.get().strip()

            if not username or not new_pw or not confirm_pw:
                messagebox.showwarning(
                    "Input Error", "Please fill in all fields."
                )
                return
            if new_pw != confirm_pw:
                messagebox.showwarning(
                    "Input Error", "New password and confirmation do not match."
                )
                return

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute("SELECT username FROM users WHERE username=?", (username,))
            row = c.fetchone()
            if not row:
                conn.close()
                messagebox.showerror(
                    "Error", "Username does not exist in the system."
                )
                return

            c.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_pw, username),
            )
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success",
                f"Password has been reset successfully for user '{username}'.",
            )
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="Save",
            font=("Times New Roman", 12, "bold"),
            bg="#2e8b57",
            fg="white",
            width=8,
            command=do_reset,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Times New Roman", 12),
            width=8,
            command=win.destroy,
        ).pack(side="left", padx=10)

    # ====================================================
    #        UPDATE PROFILE (CHANGE PASSWORD)
    # ====================================================
    def open_update_profile_window(self):
        if not self.current_user:
            messagebox.showerror(
                "Error", "You must be logged in to update your profile."
            )
            return

        win = tk.Toplevel(self.root)
        win.title("Update Profile")
        win.geometry("360x230")
        win.resizable(False, False)

        tk.Label(
            win,
            text=f"Update Profile - {self.current_user}",
            font=("Times New Roman", 14, "bold"),
        ).pack(pady=10)

        form = tk.Frame(win)
        form.pack(pady=5, padx=10)

        tk.Label(form, text="Current Password:", font=("Times New Roman", 12)).grid(
            row=0, column=0, sticky="e", padx=5, pady=5
        )
        current_entry = tk.Entry(
            form, font=("Times New Roman", 12), width=22, show="*"
        )
        current_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form, text="New Password:", font=("Times New Roman", 12)).grid(
            row=1, column=0, sticky="e", padx=5, pady=5
        )
        new_entry = tk.Entry(
            form, font=("Times New Roman", 12), width=22, show="*"
        )
        new_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form, text="Confirm Password:", font=("Times New Roman", 12)).grid(
            row=2, column=0, sticky="e", padx=5, pady=5
        )
        confirm_entry = tk.Entry(
            form, font=("Times New Roman", 12), width=22, show="*"
        )
        confirm_entry.grid(row=2, column=1, padx=5, pady=5)

        def do_update():
            cur_pw = current_entry.get().strip()
            new_pw = new_entry.get().strip()
            cf_pw = confirm_entry.get().strip()

            if not cur_pw or not new_pw or not cf_pw:
                messagebox.showwarning(
                    "Input Error", "Please fill in all fields."
                )
                return
            if new_pw != cf_pw:
                messagebox.showwarning(
                    "Input Error", "New password and confirmation do not match."
                )
                return

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            c.execute(
                "SELECT username FROM users WHERE username=? AND password=?",
                (self.current_user, cur_pw),
            )
            row = c.fetchone()
            if not row:
                conn.close()
                messagebox.showerror(
                    "Error", "Current password is incorrect."
                )
                return

            c.execute(
                "UPDATE users SET password=? WHERE username=?",
                (new_pw, self.current_user),
            )
            conn.commit()
            conn.close()

            messagebox.showinfo(
                "Success", "Your password has been updated successfully."
            )
            win.destroy()

        btn_frame = tk.Frame(win)
        btn_frame.pack(pady=10)
        tk.Button(
            btn_frame,
            text="Save",
            font=("Times New Roman", 12, "bold"),
            bg="#2e8b57",
            fg="white",
            width=8,
            command=do_update,
        ).pack(side="left", padx=10)
        tk.Button(
            btn_frame,
            text="Cancel",
            font=("Times New Roman", 12),
            width=8,
            command=win.destroy,
        ).pack(side="left", padx=10)

    # ====================================================
    #          HISTORY & REPORT WINDOWS
    # ====================================================
    def open_history_window(self):
        win = tk.Toplevel(self.root)
        win.title("Attendance History")
        win.geometry("800x400")
        win.resizable(False, False)

        filter_frame = tk.Frame(win)
        filter_frame.pack(pady=5)

        tk.Label(filter_frame, text="Student ID:", font=("Times New Roman", 11)).grid(
            row=0, column=0, padx=5, pady=5
        )
        sid_entry = tk.Entry(filter_frame, font=("Times New Roman", 11), width=15)
        sid_entry.grid(row=0, column=1, padx=5)

        tk.Label(filter_frame, text="Student Name:", font=("Times New Roman", 11)).grid(
            row=0, column=2, padx=5, pady=5
        )
        name_entry = tk.Entry(filter_frame, font=("Times New Roman", 11), width=20)
        name_entry.grid(row=0, column=3, padx=5)

        cols = ("id", "student_id", "student_name", "date", "status")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.capitalize())
            tree.column(c, width=140, anchor="center")
        tree.pack(pady=10, fill="x", padx=10)

        def load_history():
            for i in tree.get_children():
                tree.delete(i)

            sid = sid_entry.get().strip()
            sname = name_entry.get().strip()

            conn = sqlite3.connect(DB_FILE)
            c = conn.cursor()
            query = "SELECT * FROM attendance WHERE 1=1"
            params = []

            if sid:
                query += " AND student_id LIKE ?"
                params.append(f"%{sid}%")
            if sname:
                query += " AND student_name LIKE ?"
                params.append(f"%{sname}%")

            query += " ORDER BY date DESC"

            c.execute(query, params)
            rows = c.fetchall()
            conn.close()

            for r in rows:
                tree.insert("", tk.END, values=r)

        tk.Button(
            filter_frame,
            text="Search",
            font=("Times New Roman", 11),
            bg="#007bff",
            fg="white",
            width=10,
            command=load_history,
        ).grid(row=0, column=4, padx=5)

        load_history()

    def open_report_window(self):
        win = tk.Toplevel(self.root)
        win.title("Attendance Report")
        win.geometry("700x380")
        win.resizable(False, False)

        tk.Label(
            win,
            text="Attendance Summary by Student",
            font=("Times New Roman", 14, "bold"),
        ).pack(pady=10)

        cols = ("student_id", "student_name", "total", "present", "absent", "late")
        tree = ttk.Treeview(win, columns=cols, show="headings", height=12)
        for c in cols:
            tree.heading(c, text=c.replace("_", " ").title())
            tree.column(c, width=110, anchor="center")
        tree.pack(pady=10, fill="x", padx=10)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT student_id,
                   student_name,
                   COUNT(*) AS total,
                   SUM(CASE WHEN status='Present' THEN 1 ELSE 0 END) AS present_cnt,
                   SUM(CASE WHEN status='Absent' THEN 1 ELSE 0 END) AS absent_cnt,
                   SUM(CASE WHEN status='Late' THEN 1 ELSE 0 END) AS late_cnt
            FROM attendance
            GROUP BY student_id, student_name
        """)
        rows = c.fetchall()
        conn.close()

        for r in rows:
            tree.insert("", tk.END, values=r)

    # ====================================================
    #           ADMIN – MANAGE ACCOUNTS
    # ====================================================
    def build_accounts_tab(self):
        frame = self.tab_accounts

        top = tk.Frame(frame, bg="white")
        top.pack(pady=10, padx=10, fill="x")

        tk.Label(top, text="Username:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.admin_username = tk.Entry(top, font=("Times New Roman", 12), width=18)
        self.admin_username.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Password:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.admin_password = tk.Entry(
            top, font=("Times New Roman", 12), width=18, show="*"
        )
        self.admin_password.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(top, text="Role:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        self.admin_role_var = tk.StringVar()
        self.admin_role = ttk.Combobox(
            top,
            textvariable=self.admin_role_var,
            values=["admin", "teacher", "student"],
            width=10,
            font=("Times New Roman", 12),
        )
        self.admin_role.grid(row=0, column=5, padx=5, pady=5)
        self.admin_role.current(2)  # default student

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Add / Update",
            font=("Times New Roman", 11, "bold"),
            bg="#28a745",
            fg="white",
            width=14,
            command=self.admin_add_update_user,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete",
            font=("Times New Roman", 11),
            bg="#dc3545",
            fg="white",
            width=10,
            command=self.admin_delete_user,
        ).pack(side="left", padx=5)

        cols = ("username", "role")
        self.users_tree = ttk.Treeview(frame, columns=cols, show="headings", height=12)
        for c in cols:
            self.users_tree.heading(c, text=c.capitalize())
            self.users_tree.column(c, width=200, anchor="center")
        self.users_tree.pack(pady=10, fill="x", padx=10)

        self.users_tree.bind("<<TreeviewSelect>>", self.on_select_user)

        self.reload_users_table()

    def reload_users_table(self):
        for i in self.users_tree.get_children():
            self.users_tree.delete(i)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT username, role FROM users ORDER BY username")
        rows = c.fetchall()
        conn.close()

        for r in rows:
            self.users_tree.insert("", tk.END, values=r)

    def on_select_user(self, event):
        sel = self.users_tree.selection()
        if not sel:
            return
        item = self.users_tree.item(sel[0])
        username, role = item["values"]
        self.admin_username.delete(0, tk.END)
        self.admin_username.insert(0, username)
        self.admin_role_var.set(role)
        # Password không load lại (bảo mật), user sẽ nhập mới nếu muốn update

    def admin_add_update_user(self):
        username = self.admin_username.get().strip()
        password = self.admin_password.get().strip()
        role = self.admin_role_var.get().strip()

        if not username or not role:
            messagebox.showwarning(
                "Input Error", "Please enter username and select a role."
            )
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT username FROM users WHERE username=?", (username,))
        row = c.fetchone()

        if row:
            # Update
            if password:
                c.execute(
                    "UPDATE users SET password=?, role=? WHERE username=?",
                    (password, role, username),
                )
            else:
                c.execute(
                    "UPDATE users SET role=? WHERE username=?",
                    (role, username),
                )
        else:
            if not password:
                messagebox.showwarning(
                    "Input Error", "Please enter a password for new account."
                )
                conn.close()
                return
            c.execute(
                "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                (username, password, role),
            )

        conn.commit()
        conn.close()
        self.reload_users_table()
        messagebox.showinfo("Success", "Account has been saved successfully.")

    def admin_delete_user(self):
        sel = self.users_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select an account to delete.")
            return

        item = self.users_tree.item(sel[0])
        username = item["values"][0]

        if username == "admin":
            messagebox.showwarning("Warning", "Cannot delete default admin account.")
            return

        if not messagebox.askyesno(
            "Confirm", f"Delete user account '{username}'?"
        ):
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
        conn.close()

        self.reload_users_table()
        messagebox.showinfo("Deleted", "Account deleted successfully.")

    # ====================================================
    #           ADMIN – MANAGE COURSES
    # ====================================================
    def build_courses_tab(self):
        frame = self.tab_courses

        top = tk.Frame(frame, bg="white")
        top.pack(pady=10, padx=10, fill="x")

        tk.Label(top, text="Course Code:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.course_code = tk.Entry(top, font=("Times New Roman", 12), width=18)
        self.course_code.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Course Name:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.course_name = tk.Entry(top, font=("Times New Roman", 12), width=25)
        self.course_name.grid(row=0, column=3, padx=5, pady=5)

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Add Course",
            font=("Times New Roman", 11, "bold"),
            bg="#28a745",
            fg="white",
            width=12,
            command=self.admin_add_course,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete Course",
            font=("Times New Roman", 11),
            bg="#dc3545",
            fg="white",
            width=12,
            command=self.admin_delete_course,
        ).pack(side="left", padx=5)

        cols = ("id", "course_code", "course_name")
        self.courses_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=12
        )
        for c in cols:
            self.courses_tree.heading(c, text=c.replace("_", " ").title())
            self.courses_tree.column(c, width=180, anchor="center")
        self.courses_tree.pack(pady=10, fill="x", padx=10)

        self.courses_tree.bind("<<TreeviewSelect>>", self.on_select_course)

        self.reload_courses_table()

    def reload_courses_table(self):
        for i in self.courses_tree.get_children():
            self.courses_tree.delete(i)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, course_code, course_name FROM courses ORDER BY id")
        rows = c.fetchall()
        conn.close()

        for r in rows:
            self.courses_tree.insert("", tk.END, values=r)

    def on_select_course(self, event):
        sel = self.courses_tree.selection()
        if not sel:
            return
        item = self.courses_tree.item(sel[0])
        _, code, name = item["values"]
        self.course_code.delete(0, tk.END)
        self.course_code.insert(0, code)
        self.course_name.delete(0, tk.END)
        self.course_name.insert(0, name)

    def admin_add_course(self):
        code = self.course_code.get().strip()
        name = self.course_name.get().strip()

        if not code or not name:
            messagebox.showwarning(
                "Input Error", "Please enter course code and course name."
            )
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO courses (course_code, course_name) VALUES (?, ?)",
            (code, name),
        )
        conn.commit()
        conn.close()

        self.reload_courses_table()
        messagebox.showinfo("Success", "Course added successfully.")

    def admin_delete_course(self):
        sel = self.courses_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a course to delete.")
            return

        item = self.courses_tree.item(sel[0])
        course_id = item["values"][0]

        if not messagebox.askyesno("Confirm", "Delete selected course?"):
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM courses WHERE id=?", (course_id,))
        conn.commit()
        conn.close()

        self.reload_courses_table()
        messagebox.showinfo("Deleted", "Course deleted successfully.")

    # ====================================================
    #           ADMIN – MANAGE CLASSES
    # ====================================================
    def build_classes_tab(self):
        frame = self.tab_classes

        top = tk.Frame(frame, bg="white")
        top.pack(pady=10, padx=10, fill="x")

        tk.Label(top, text="Class Code:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=0, padx=5, pady=5, sticky="e"
        )
        self.class_code = tk.Entry(top, font=("Times New Roman", 12), width=15)
        self.class_code.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(top, text="Class Name:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=2, padx=5, pady=5, sticky="e"
        )
        self.class_name = tk.Entry(top, font=("Times New Roman", 12), width=20)
        self.class_name.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(top, text="Course:", font=("Times New Roman", 12), bg="white").grid(
            row=0, column=4, padx=5, pady=5, sticky="e"
        )
        self.class_course_var = tk.StringVar()
        self.class_course_combo = ttk.Combobox(
            top, textvariable=self.class_course_var, width=18, font=("Times New Roman", 12)
        )
        self.class_course_combo.grid(row=0, column=5, padx=5, pady=5)

        btn_frame = tk.Frame(frame, bg="white")
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="Add Class",
            font=("Times New Roman", 11, "bold"),
            bg="#28a745",
            fg="white",
            width=12,
            command=self.admin_add_class,
        ).pack(side="left", padx=5)

        tk.Button(
            btn_frame,
            text="Delete Class",
            font=("Times New Roman", 11),
            bg="#dc3545",
            fg="white",
            width=12,
            command=self.admin_delete_class,
        ).pack(side="left", padx=5)

        cols = ("id", "class_code", "class_name", "course_name")
        self.classes_tree = ttk.Treeview(
            frame, columns=cols, show="headings", height=12
        )
        for c in cols:
            self.classes_tree.heading(c, text=c.replace("_", " ").title())
            self.classes_tree.column(c, width=160, anchor="center")
        self.classes_tree.pack(pady=10, fill="x", padx=10)

        self.classes_tree.bind("<<TreeviewSelect>>", self.on_select_class)

        self.reload_classes_table()
        self.reload_courses_to_combo()

    def reload_courses_to_combo(self):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("SELECT id, course_name FROM courses ORDER BY course_name")
        rows = c.fetchall()
        conn.close()

        self.course_list = rows
        names = [r[1] for r in rows]
        self.class_course_combo["values"] = names

    def reload_classes_table(self):
        for i in self.classes_tree.get_children():
            self.classes_tree.delete(i)

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("""
            SELECT classes.id, classes.class_code, classes.class_name,
                   COALESCE(courses.course_name, '')
            FROM classes
            LEFT JOIN courses ON classes.course_id = courses.id
            ORDER BY classes.id
        """)
        rows = c.fetchall()
        conn.close()

        for r in rows:
            self.classes_tree.insert("", tk.END, values=r)

    def on_select_class(self, event):
        sel = self.classes_tree.selection()
        if not sel:
            return
        item = self.classes_tree.item(sel[0])
        _, code, name, course_name = item["values"]
        self.class_code.delete(0, tk.END)
        self.class_code.insert(0, code)
        self.class_name.delete(0, tk.END)
        self.class_name.insert(0, name)
        self.class_course_var.set(course_name)

    def admin_add_class(self):
        code = self.class_code.get().strip()
        name = self.class_name.get().strip()
        cname = self.class_course_var.get().strip()

        if not code or not name:
            messagebox.showwarning(
                "Input Error", "Please enter class code and class name."
            )
            return

        course_id = None
        if cname:
            for (cid, n) in getattr(self, "course_list", []):
                if n == cname:
                    course_id = cid
                    break

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute(
            "INSERT INTO classes (class_code, class_name, course_id) VALUES (?, ?, ?)",
            (code, name, course_id),
        )
        conn.commit()
        conn.close()

        self.reload_classes_table()
        messagebox.showinfo("Success", "Class added successfully.")

    def admin_delete_class(self):
        sel = self.classes_tree.selection()
        if not sel:
            messagebox.showwarning("Warning", "Please select a class to delete.")
            return

        item = self.classes_tree.item(sel[0])
        class_id = item["values"][0]

        if not messagebox.askyesno("Confirm", "Delete selected class?"):
            return

        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("DELETE FROM classes WHERE id=?", (class_id,))
        conn.commit()
        conn.close()

        self.reload_classes_table()
        messagebox.showinfo("Deleted", "Class deleted successfully.")


# =================== RUN ===================
if __name__ == "__main__":
    root = tk.Tk()
    app = AttendanceApp(root)
    root.mainloop()
