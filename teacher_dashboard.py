import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import csv
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class TeacherDashboard:
    # List of valid subjects organized by semester
    SUBJECTS_BY_SEM = {
        3: ["MATHS3", "DSA", "DBMS", "PCPF", "PCOM"],
        4: ["MATHS4", "OS", "CNND", "COA", "AT"]
    }
    
    # Combined list of all subjects
    SUBJECTS = ["MATHS3", "DSA", "DBMS", "PCPF", "PCOM", "MATHS4", "OS", "CNND", "COA", "AT"]
    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Teacher Dashboard - {username}")
        self.root.geometry("1200x800")
        
        # Apply a professional color scheme
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0')
        self.style.configure('TButton', background='#3498db', foreground='white')
        self.style.map('TButton', background=[('active', '#2980b9')])
        
        self.root.configure(bg="#f0f0f0")
        
        # Initialize database connection and create table if not exists
        self.conn = sqlite3.connect('student_results.db')
        self.cursor = self.conn.cursor()
        
        # Create tables if they don't exist
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK (role IN ('student', 'teacher')) NOT NULL,
            full_name TEXT NOT NULL
        )
        ''')
        
        # Create default admin user if not exists
        self.cursor.execute('''
        INSERT OR IGNORE INTO users (username, password, role, full_name)
        VALUES (?, ?, ?, ?)
        ''', ('admin', 'admin123', 'teacher', 'Administrator'))
        
        # Generate the subject list for the SQL constraint
        subjects_list = "'" + "', '".join(self.SUBJECTS) + "'"
        
        self.cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS results (
            std_id TEXT,
            student_name TEXT NOT NULL,
            roll_no TEXT NOT NULL,
            subject TEXT NOT NULL CHECK (subject IN ({subjects_list})),
            marks INTEGER NOT NULL CHECK (marks >= 0 AND marks <= 100),
            semester INTEGER CHECK (semester IN (3, 4)),
            exam_type TEXT CHECK (exam_type IN ('IA1', 'IA2', 'SEM')),
            added_by TEXT NOT NULL,
            added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (std_id, subject, semester, exam_type),
            FOREIGN KEY (added_by) REFERENCES users(username),
            FOREIGN KEY (std_id) REFERENCES users(username)
        )
        ''')
        self.conn.commit()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Setup main container with gradient effect
        self.main_container = tk.Frame(self.root, bg="#f0f0f0")
        self.main_container.pack(fill=tk.BOTH, expand=True)
        
        # Setup header
        self.setup_header()
        
        # Setup content area
        self.setup_content()
        
        # Current marks frame reference (to be updated when semester changes)
        self.marks_frame = None
        self.marks_entries = {}
    
    def setup_header(self):
        header_frame = tk.Frame(self.main_container, bg="#2c3e50", height=80)
        header_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Title with shadow effect
        title_label = tk.Label(header_frame, text="TEACHER DASHBOARD", 
                             font=("Helvetica", 24, "bold"), bg="#2c3e50", fg="white")
        title_label.pack(side=tk.LEFT, padx=30, pady=15)
        
        # Logout button
        logout_btn = tk.Button(header_frame, text="Logout", font=("Helvetica", 12, "bold"),
                             bg="#e74c3c", fg="white", command=self.logout,
                             relief="flat", padx=20, pady=8,
                             activebackground="#c0392b")
        logout_btn.pack(side=tk.RIGHT, padx=30, pady=15)
    
    def setup_content(self):
        # Create main content frame with shadow effect
        content_frame = ttk.Frame(self.main_container)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=20)
        
        # Create navigation buttons
        nav_frame = ttk.Frame(content_frame)
        nav_frame.pack(fill=tk.X, pady=(0, 30))
        
        # Configure styles
        style = ttk.Style()
        style.configure("Custom.TButton", 
                      font=("Helvetica", 16, "bold"),
                      padding=15)
        
        # Add Result button
        self.add_result_btn = ttk.Button(nav_frame, text="Add Result", 
                                       style="Custom.TButton",
                                       command=self.show_add_result)
        self.add_result_btn.pack(side=tk.LEFT, padx=15)
        
        # View Result button
        self.view_result_btn = ttk.Button(nav_frame, text="View Result", 
                                        style="Custom.TButton",
                                        command=self.show_view_result)
        self.view_result_btn.pack(side=tk.LEFT, padx=15)
        
        # Rank List button
        self.rank_list_btn = ttk.Button(nav_frame, text="Rank List", 
                                      style="Custom.TButton",
                                      command=self.show_rank_list)
        self.rank_list_btn.pack(side=tk.LEFT, padx=15)
        
        # Change Password button
        self.change_pwd_btn = ttk.Button(nav_frame, text="Change Password",
                                       style="Custom.TButton",
                                       command=self.show_change_password)
        self.change_pwd_btn.pack(side=tk.LEFT, padx=15)
        
        # Content area with modern border
        self.content_area = ttk.Frame(content_frame)
        self.content_area.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Show add result by default
        self.show_add_result()
    
    def show_add_result(self):
        self.clear_content()
        self.setup_add_result_tab()
        # Update button states
        self.add_result_btn.state(['!disabled'])
        self.view_result_btn.state(['!disabled'])
        self.rank_list_btn.state(['!disabled'])
        
    def show_view_result(self):
        self.clear_content()
        self.show_view_result_tab()
        # Update button states
        self.add_result_btn.state(['!disabled'])
        self.view_result_btn.state(['!disabled'])
        self.rank_list_btn.state(['!disabled'])
    
    def clear_content(self):
        for widget in self.content_area.winfo_children():
            widget.destroy()
    
    def setup_add_result_tab(self):
        style = ttk.Style()
        style.configure("Custom.TLabelframe", background="#ffffff", padding=15)
        style.configure("Custom.TLabelframe.Label", font=("Helvetica", 12, "bold"))
        style.configure("Info.TLabel", font=("Helvetica", 12))
        style.configure("Info.TEntry", font=("Helvetica", 12))
        style.configure("Action.TButton", font=("Helvetica", 12, "bold"), padding=5)
        
        # Main Frame
        main_frame = ttk.LabelFrame(self.content_area, text="Add New Result", 
                                  style="Custom.TLabelframe")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create two columns
        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        
        # Student Info Frame (Left side)
        info_frame = ttk.LabelFrame(left_frame, text="Student Information",
                                  style="Custom.TLabelframe")
        info_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Student Information Fields
        ttk.Label(info_frame, text="Student Name:", style="Info.TLabel").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.name_entry = ttk.Entry(info_frame, style="Info.TEntry")
        self.name_entry.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        
        ttk.Label(info_frame, text="Student ID:", style="Info.TLabel").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.std_id_entry = ttk.Entry(info_frame, style="Info.TEntry")
        self.std_id_entry.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        # Bind the student ID entry to fetch details
        self.std_id_entry.bind('<FocusOut>', self.fetch_student_details)
        
        ttk.Label(info_frame, text="Roll No:", style="Info.TLabel").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        self.roll_no_entry = ttk.Entry(info_frame, style="Info.TEntry")
        self.roll_no_entry.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        
        # Exam Information Frame (additional frame in left column)
        exam_frame = ttk.LabelFrame(left_frame, text="Exam Information",
                                  style="Custom.TLabelframe")
        exam_frame.pack(fill=tk.BOTH, expand=False, pady=10)
        
        # Semester selection
        ttk.Label(exam_frame, text="Semester:", style="Info.TLabel").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.semester_var = tk.StringVar(value="3")
        semester_combo = ttk.Combobox(exam_frame, textvariable=self.semester_var, 
                                    values=["3", "4"], state="readonly",
                                    style="Info.TEntry")
        semester_combo.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        # Bind semester change event
        semester_combo.bind("<<ComboboxSelected>>", self.update_subject_entries)
        
        # Exam Type selection
        ttk.Label(exam_frame, text="Exam Type:", style="Info.TLabel").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        self.exam_type_var = tk.StringVar(value="IA1")
        exam_type_combo = ttk.Combobox(exam_frame, textvariable=self.exam_type_var, 
                                     values=["IA1", "IA2", "SEM"], state="readonly",
                                     style="Info.TEntry")
        exam_type_combo.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        
        # Configure grid weights
        info_frame.grid_columnconfigure(1, weight=1)
        exam_frame.grid_columnconfigure(1, weight=1)
        
        # Marks Frame (Right side) with scrollbar for many subjects
        self.marks_labelframe = ttk.LabelFrame(right_frame, text="Subject Marks", style="Custom.TLabelframe")
        self.marks_labelframe.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Create a canvas with scrollbar for the marks
        self.marks_canvas = tk.Canvas(self.marks_labelframe, bg="#ffffff", highlightthickness=0)
        self.marks_scrollbar = ttk.Scrollbar(self.marks_labelframe, orient="vertical", command=self.marks_canvas.yview)
        
        self.marks_frame = ttk.Frame(self.marks_canvas, style="Custom.TFrame")
        
        # Initialize marks entries
        self.update_subject_entries()
        
        # Buttons Frame (Bottom)
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        # Add buttons with consistent styling - stacked vertically
        submit_btn = ttk.Button(button_frame, text="Submit Result", style="Action.TButton",
                  command=self.add_result)
        submit_btn.pack(fill=tk.X, pady=5)
        
        import_btn = ttk.Button(button_frame, text="Import CSV", style="Action.TButton",
                  command=self.import_csv)
        import_btn.pack(fill=tk.X, pady=5)
        
        clear_btn = ttk.Button(button_frame, text="Clear Form", style="Action.TButton",
                  command=self.clear_form)
        clear_btn.pack(fill=tk.X, pady=5)
    
    def update_subject_entries(self, event=None):
        # Get the current semester
        sem = int(self.semester_var.get())
        
        # Clear existing marks frame
        if hasattr(self, 'marks_frame') and self.marks_frame:
            for widget in self.marks_frame.winfo_children():
                widget.destroy()
            
        # Create a new frame
        self.marks_frame = ttk.Frame(self.marks_canvas, style="Custom.TFrame")
        self.marks_frame.bind("<Configure>", lambda e: self.marks_canvas.configure(scrollregion=self.marks_canvas.bbox("all")))
        
        self.marks_canvas.create_window((0, 0), window=self.marks_frame, anchor="nw")
        self.marks_canvas.configure(yscrollcommand=self.marks_scrollbar.set)
        
        # Pack canvas and scrollbar
        self.marks_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.marks_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Create mark entries only for the subjects in the selected semester
        self.marks_entries = {}
        semester_subjects = self.SUBJECTS_BY_SEM[sem]
        
        for i, subject in enumerate(semester_subjects):
            # Create frame for each subject row
            row_frame = ttk.Frame(self.marks_frame)
            row_frame.pack(fill=tk.X, padx=5, pady=5)
            
            # Add subject label
            ttk.Label(row_frame, text=f"{subject}:", style="Info.TLabel").pack(side=tk.LEFT, padx=(0, 10))
            
            # Add entry field
            entry = ttk.Entry(row_frame, style="Info.TEntry", width=20)
            entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
            self.marks_entries[subject] = entry
        
        # Configure grid weights
        self.marks_frame.grid_columnconfigure(1, weight=1)
    
    def show_view_result_tab(self):
        # Clear everything first
        self.clear_content()
        
        # Create main frame
        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Search Results Section
        search_frame = ttk.LabelFrame(main_frame, text="Search Results")
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a frame for search controls
        controls_frame = ttk.Frame(search_frame)
        controls_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Search Entry
        ttk.Label(controls_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(controls_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, padx=(0, 20))
        
        # Subject Filter
        ttk.Label(controls_frame, text="Subject:").pack(side=tk.LEFT, padx=(0, 5))
        self.subject_filter = tk.StringVar(value="All")
        subjects = ["All"] + self.SUBJECTS
        self.subject_filter_combo = ttk.Combobox(controls_frame, textvariable=self.subject_filter, 
                                               values=subjects, state="readonly", width=25)
        self.subject_filter_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Semester Filter
        ttk.Label(controls_frame, text="Semester:").pack(side=tk.LEFT, padx=(0, 5))
        self.semester_filter = tk.StringVar(value="All")
        self.semester_combo = ttk.Combobox(controls_frame, textvariable=self.semester_filter,
                                         values=["All", "3", "4"], state="readonly", width=25)
        self.semester_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Exam Type Filter
        ttk.Label(controls_frame, text="Exam Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.exam_type_filter = tk.StringVar(value="All")
        exam_types = ttk.Combobox(controls_frame, textvariable=self.exam_type_filter,
                                values=["All", "IA1", "IA2", "SEM"], state="readonly", width=25)
        exam_types.pack(side=tk.LEFT)
        
        # Buttons Frame
        button_frame = ttk.Frame(search_frame)
        button_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Export and Delete buttons
        export_btn = ttk.Button(button_frame, text="Export to CSV", command=self.export_to_csv)
        export_btn.pack(side=tk.LEFT, padx=5)
        
        delete_btn = ttk.Button(button_frame, text="Delete Selected", command=self.delete_selected_records)
        delete_btn.pack(side=tk.LEFT, padx=5)
        
        # Results Preview Section
        preview_frame = ttk.LabelFrame(main_frame, text="Results Preview")
        preview_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview with scrollbar
        tree_frame = ttk.Frame(preview_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = ("Name", "Student ID", "Roll No", "Subject", "Marks", "Semester", "Exam Type")
        self.results_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Set column headings and widths
        for col in columns:
            self.results_tree.heading(col, text=col)
            self.results_tree.column(col, width=100)  # Adjust width as needed
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        self.results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind search and filter events
        self.search_var.trace('w', self.filter_results)
        self.subject_filter.trace('w', self.filter_results)
        self.semester_filter.trace('w', self.filter_results)
        self.exam_type_filter.trace('w', self.filter_results)
        
        # Bind semester change to update subject filter
        self.semester_combo.bind('<<ComboboxSelected>>', self.update_subject_filter)
        
        # Load initial results
        self.load_results()
    
    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            if hasattr(self, 'conn'):
                self.conn.close()
            self.root.destroy()
            # Import and create new login window
            import login
            new_root = tk.Tk()
            login.LoginWindow(new_root)
            new_root.mainloop()
    
    def filter_results(self, *args):
        """Filter results based on search text and dropdown selections"""
        search_text = self.search_var.get().lower()
        subject = self.subject_filter.get()
        semester = self.semester_filter.get()
        exam_type = self.exam_type_filter.get()
        
        # Clear current display
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
        
        try:
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # Build query with filters - using correct column name std_id
            query = """
            SELECT u.full_name, r.std_id, r.roll_no, r.subject, r.marks, r.semester, r.exam_type
            FROM results r
            JOIN users u ON r.std_id = u.username
            WHERE 1=1
            """
            params = []
            
            if subject != "All":
                query += " AND r.subject = ?"
                params.append(subject)
            
            if semester != "All":
                query += " AND r.semester = ?"
                params.append(semester)
                
            if exam_type != "All":
                query += " AND r.exam_type = ?"
                params.append(exam_type)
                
            query += " ORDER BY r.roll_no, r.subject, r.exam_type"
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Filter by search text and add to treeview
            for result in results:
                if (search_text == "" or 
                    search_text in str(result[0]).lower() or  # name
                    search_text in str(result[1]).lower() or  # std_id
                    search_text in str(result[2]).lower()):   # roll_no
                    self.results_tree.insert('', 'end', values=result)
                    
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def load_results(self):
        """Load all results into the treeview"""
        # Clear existing items
        for item in self.results_tree.get_children():
            self.results_tree.delete(item)
            
        try:
            # Connect to database
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # Get all results with student names - ordered by std_id
            query = """
            SELECT u.full_name, r.std_id, r.roll_no, r.subject, r.marks, r.semester, r.exam_type
            FROM results r
            JOIN users u ON r.std_id = u.username
            ORDER BY r.std_id ASC, r.roll_no, r.subject, r.exam_type
            """
            cursor.execute(query)
            results = cursor.fetchall()
            
            # Insert into treeview
            for result in results:
                self.results_tree.insert('', 'end', values=result)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def add_result(self):
        try:
            # Get values from entries
            std_id = self.std_id_entry.get().strip()
            name = self.name_entry.get().strip()
            roll_no = self.roll_no_entry.get().strip()
            semester = int(self.semester_var.get())
            exam_type = self.exam_type_var.get()
            
            # Validate inputs
            if not all([std_id, name, roll_no]):
                messagebox.showerror("Error", "Please fill all student information fields!")
                return
            
            # Validate and collect marks
            marks_data = []
            for subject, entry in self.marks_entries.items():
                marks = entry.get().strip()
                if not marks:
                    messagebox.showerror("Error", f"Please enter marks for {subject}!")
                    return
                try:
                    marks = float(marks)
                    if not (0 <= marks <= 100):
                        messagebox.showerror("Error", f"Marks for {subject} must be between 0 and 100!")
                        return
                    marks_data.append((std_id, name, roll_no, subject, marks, semester, exam_type, self.username))
                except ValueError:
                    messagebox.showerror("Error", f"Invalid marks for {subject}! Please enter a number.")
                    return
            
            # Connect to database
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            try:
                # Insert all marks
                cursor.executemany('''
                INSERT OR REPLACE INTO results 
                (std_id, student_name, roll_no, subject, marks, semester, exam_type, added_by)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', marks_data)
                
                # Check if student user exists
                cursor.execute('''
                SELECT id FROM users WHERE username = ? AND role = 'student'
                ''', (std_id,))
                
                if not cursor.fetchone():
                    # Create student user account using std_id as username
                    cursor.execute('''
                    INSERT INTO users (username, password, role, full_name)
                    VALUES (?, ?, 'student', ?)
                    ''', (std_id, 'student123', name))
                
                conn.commit()
                messagebox.showinfo("Success", "Results added successfully!")
                
                # Clear form
                self.clear_form()
                
                # Refresh results display
                self.load_results()
                
            except sqlite3.Error as e:
                conn.rollback()
                messagebox.showerror("Database Error", f"Failed to add results: {str(e)}")
            finally:
                conn.close()
                
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
    
    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.std_id_entry.delete(0, tk.END)
        self.roll_no_entry.delete(0, tk.END)
        self.semester_var.set("3")
        self.exam_type_var.set("IA1")
        # Update subject entries for semester 3
        self.update_subject_entries()
    
    def validate_marks(self, marks):
        try:
            marks = float(marks)
            return 0 <= marks <= 100
        except ValueError:
            return False
    
    def import_csv(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return
        
        try:
            preview_window = tk.Toplevel(self.root)
            preview_window.title("CSV Preview")
            preview_window.geometry("800x500")  # Make it larger to accommodate more columns
            
            # Preview CSV content
            with open(file_path, 'r') as file:
                reader = csv.DictReader(file)
                preview_data = list(reader)
                
                # Check required columns
                required_columns = ['std_id', 'student_name', 'roll_no', 'subject', 'marks', 'semester', 'exam_type']
                missing_columns = [col for col in required_columns if col not in preview_data[0]]
                
                if missing_columns:
                    messagebox.showerror("Error", f"CSV is missing required columns: {', '.join(missing_columns)}")
                    preview_window.destroy()
                    return
                
                # Create preview treeview
                preview_tree = ttk.Treeview(preview_window, columns=list(preview_data[0].keys()), show="headings")
                for col in preview_data[0].keys():
                    preview_tree.heading(col, text=col)
                    preview_tree.column(col, width=100)
                
                # Add preview data
                for row in preview_data:
                    preview_tree.insert("", tk.END, values=list(row.values()))
                
                # Add scrollbars
                y_scrollbar = ttk.Scrollbar(preview_window, orient="vertical", command=preview_tree.yview)
                x_scrollbar = ttk.Scrollbar(preview_window, orient="horizontal", command=preview_tree.xview)
                
                # Configure scrollbars
                preview_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
                
                # Pack preview and scrollbars
                preview_tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
                y_scrollbar.pack(fill=tk.Y, side=tk.RIGHT)
                x_scrollbar.pack(fill=tk.X, side=tk.BOTTOM)
                
                # Confirm button
                if messagebox.askyesno("Confirm Import", "Do you want to import this data?"):
                    # Process and import data
                    for row in preview_data:
                        try:
                            # Validate semester
                            semester = int(row['semester'])
                            if semester not in [3, 4]:
                                raise ValueError(f"Invalid semester: {semester}")
                            
                            # Validate exam_type
                            exam_type = row['exam_type']
                            if exam_type not in ['IA1', 'IA2', 'SEM']:
                                raise ValueError(f"Invalid exam type: {exam_type}")
                            
                            # Validate subject
                            subject = row['subject']
                            if subject not in self.SUBJECTS:
                                raise ValueError(f"Invalid subject: {subject}. Must be one of: {', '.join(self.SUBJECTS)}")
                            
                            # Validate marks
                            marks = float(row['marks'])
                            if not (0 <= marks <= 100):
                                raise ValueError(f"Invalid marks: {marks}")
                            
                            # Insert into database
                            self.cursor.execute('''
                                INSERT OR REPLACE INTO results 
                                (std_id, student_name, roll_no, subject, marks, semester, exam_type, added_by)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                row['std_id'],
                                row['student_name'],
                                row['roll_no'],
                                subject,
                                marks,
                                semester,
                                exam_type,
                                self.username
                            ))
                            
                            # Check if student user exists
                            self.cursor.execute('''
                                SELECT id FROM users WHERE username = ? AND role = 'student'
                            ''', (row['std_id'],))
                            
                            if not self.cursor.fetchone():
                                # Create student user account
                                self.cursor.execute('''
                                    INSERT INTO users (username, password, role, full_name)
                                    VALUES (?, ?, 'student', ?)
                                ''', (row['std_id'], 'student123', row['student_name']))
                        except Exception as e:
                            messagebox.showerror("Error", f"Error processing row for {row['std_id']}: {str(e)}")
                            self.conn.rollback()
                            preview_window.destroy()
                            return
                    
                    self.conn.commit()
                    messagebox.showinfo("Success", "CSV imported successfully!")
                    self.load_results()
            
            preview_window.destroy()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to import CSV: {str(e)}")
            if 'preview_window' in locals():
                preview_window.destroy()
    
    def export_to_csv(self):
        """Export filtered results to CSV file"""
        if not self.results_tree.get_children():
            messagebox.showinfo("Export", "No results to export!")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", '*.csv')],
                title="Export Results"
            )
            
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    # Write headers
                    headers = [self.results_tree.heading(col)['text'] for col in self.results_tree['columns']]
                    writer.writerow(headers)
                    
                    # Write data
                    for item in self.results_tree.get_children():
                        row = self.results_tree.item(item)['values']
                        writer.writerow(row)
                        
                messagebox.showinfo("Export Successful", f"Results exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")
    
    def delete_selected_records(self):
        """Delete selected records from the database and treeview"""
        selected_items = self.results_tree.selection()
        if not selected_items:
            messagebox.showinfo("Delete", "Please select records to delete!")
            return
            
        if not messagebox.askyesno("Confirm Delete", 
                                  "Are you sure you want to delete the selected records?"):
            return
            
        try:
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            for item in selected_items:
                values = self.results_tree.item(item)['values']
                # Delete from database - using correct column name std_id
                cursor.execute("""
                    DELETE FROM results 
                    WHERE std_id = ? AND subject = ? AND semester = ? AND exam_type = ?
                """, (values[1], values[3], values[5], values[6]))
                
                # Remove from treeview
                self.results_tree.delete(item)
                
            conn.commit()
            messagebox.showinfo("Success", "Selected records have been deleted!")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()
    
    def on_closing(self):
        if hasattr(self, 'conn'):
            self.conn.close()
        self.root.destroy()

    def show_change_password(self):
        # Create change password dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("600x500")  # Increased window size
        dialog.configure(bg="#f0f0f0")
        
        # Make dialog modal
        dialog.transient(self.root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 300,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 250
        ))
        
        # Create main frame with padding
        main_frame = ttk.LabelFrame(dialog, text="Change Password", style="Custom.TLabelframe")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=30)
        
        # Style configuration
        style = ttk.Style()
        style.configure("Password.TLabel", font=("Helvetica", 12))
        style.configure("Password.TEntry", font=("Helvetica", 12))
        style.configure("Password.TButton", font=("Helvetica", 12, "bold"), padding=10)
        
        # Password visibility states
        show_current = tk.BooleanVar(value=False)
        show_new = tk.BooleanVar(value=False)
        show_confirm = tk.BooleanVar(value=False)
        
        def toggle_password_visibility(entry, var):
            if var.get():
                entry.config(show="")
            else:
                entry.config(show="*")
        
        # Current password frame
        current_frame = ttk.Frame(main_frame)
        current_frame.pack(fill=tk.X, pady=(20,10))
        ttk.Label(current_frame, text="Current Password:", style="Password.TLabel").pack(side=tk.LEFT, padx=5)
        current_pwd = ttk.Entry(current_frame, font=("Helvetica", 12), show="*", width=30)
        current_pwd.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(current_frame, text="Show", variable=show_current, 
                       command=lambda: toggle_password_visibility(current_pwd, show_current)).pack(side=tk.LEFT, padx=5)
        
        # New password frame
        new_frame = ttk.Frame(main_frame)
        new_frame.pack(fill=tk.X, pady=10)
        ttk.Label(new_frame, text="New Password:", style="Password.TLabel").pack(side=tk.LEFT, padx=5)
        new_pwd = ttk.Entry(new_frame, font=("Helvetica", 12), show="*", width=30)
        new_pwd.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(new_frame, text="Show", variable=show_new,
                       command=lambda: toggle_password_visibility(new_pwd, show_new)).pack(side=tk.LEFT, padx=5)
        
        # Confirm password frame
        confirm_frame = ttk.Frame(main_frame)
        confirm_frame.pack(fill=tk.X, pady=10)
        ttk.Label(confirm_frame, text="Confirm Password:", style="Password.TLabel").pack(side=tk.LEFT, padx=5)
        confirm_pwd = ttk.Entry(confirm_frame, font=("Helvetica", 12), show="*", width=30)
        confirm_pwd.pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(confirm_frame, text="Show", variable=show_confirm,
                       command=lambda: toggle_password_visibility(confirm_pwd, show_confirm)).pack(side=tk.LEFT, padx=5)
        
        # Password requirements label
        req_label = ttk.Label(main_frame, 
                            text="Password Requirements:\n• Minimum 6 characters\n• At least one number\n• At least one uppercase letter",
                            style="Password.TLabel", justify=tk.LEFT)
        req_label.pack(pady=20, anchor=tk.W, padx=5)
        
        def change_password():
            current = current_pwd.get()
            new = new_pwd.get()
            confirm = confirm_pwd.get()
            
            if not all([current, new, confirm]):
                messagebox.showerror("Error", "All fields are required!")
                return
            
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
            
            try:
                # Verify current password
                self.cursor.execute("SELECT password FROM users WHERE username = ?", (self.username,))
                stored_password = self.cursor.fetchone()
                
                if not stored_password or stored_password[0] != current:
                    messagebox.showerror("Error", "Current password is incorrect!")
                    return
                
                # Update password
                self.cursor.execute("UPDATE users SET password = ? WHERE username = ?", (new, self.username))
                self.conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!")
                dialog.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to change password: {str(e)}")
                self.conn.rollback()
        
        # Buttons frame with larger buttons
        btn_frame = ttk.Frame(main_frame)
        btn_frame.pack(fill=tk.X, pady=30)
        
        # Change button - larger and more prominent
        change_btn = ttk.Button(btn_frame, text="Change Password", 
                              style="Password.TButton",
                              command=change_password)
        change_btn.pack(side=tk.LEFT, padx=20, expand=True)
        
        # Cancel button - larger and more prominent
        cancel_btn = ttk.Button(btn_frame, text="Cancel", 
                              style="Password.TButton",
                              command=dialog.destroy)
        cancel_btn.pack(side=tk.LEFT, padx=20, expand=True)
        
        # Focus on first entry
        current_pwd.focus()

    def update_subject_filter(self, *args):
        """Update subject filter based on selected semester"""
        semester = self.rank_semester_filter.get()
        subjects = []
        
        if semester == "All":
            subjects = ["All"] + self.SUBJECTS
        else:
            subjects = ["All"] + self.SUBJECTS_BY_SEM[int(semester)]
        
        self.rank_subject_combo['values'] = subjects
        self.rank_subject_filter.set("All")

    def setup_rank_list_tab(self):
        # Clear existing content
        self.clear_content()
        
        # Create main frame
        main_frame = ttk.Frame(self.content_area)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Create filters frame
        filters_frame = ttk.LabelFrame(main_frame, text="Filters")
        filters_frame.pack(fill=tk.X, padx=5, pady=5)
        
        # Create a frame for filters
        filter_controls = ttk.Frame(filters_frame)
        filter_controls.pack(fill=tk.X, padx=10, pady=10)
        
        # Semester Filter
        ttk.Label(filter_controls, text="Semester:").pack(side=tk.LEFT, padx=(0, 5))
        self.rank_semester_filter = tk.StringVar(value="All")
        semester_combo = ttk.Combobox(filter_controls, textvariable=self.rank_semester_filter,
                                    values=["All", "3", "4"], state="readonly", width=15)
        semester_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Subject Filter
        ttk.Label(filter_controls, text="Subject:").pack(side=tk.LEFT, padx=(0, 5))
        self.rank_subject_filter = tk.StringVar(value="All")
        self.rank_subject_combo = ttk.Combobox(filter_controls, textvariable=self.rank_subject_filter,
                                              values=["All"], state="readonly", width=15)
        self.rank_subject_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Exam Type Filter
        ttk.Label(filter_controls, text="Exam Type:").pack(side=tk.LEFT, padx=(0, 5))
        self.rank_exam_type_filter = tk.StringVar(value="All")
        exam_type_combo = ttk.Combobox(filter_controls, textvariable=self.rank_exam_type_filter,
                                      values=["All", "IA1", "IA2", "SEM"], state="readonly", width=15)
        exam_type_combo.pack(side=tk.LEFT, padx=(0, 20))
        
        # Export buttons frame
        export_frame = ttk.Frame(filters_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=10)
        
        # Export buttons
        ttk.Button(export_frame, text="Export to CSV", command=self.export_rank_list_csv).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Export to PDF", command=self.export_rank_list_pdf).pack(side=tk.LEFT, padx=5)
        
        # Create Treeview for rank list
        tree_frame = ttk.Frame(main_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create Treeview
        columns = ("Rank", "Student ID", "Name", "Roll No", "Total Marks", "Average", "Semester")
        self.rank_tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        
        # Set column headings and widths
        self.rank_tree.heading("Rank", text="Rank")
        self.rank_tree.heading("Student ID", text="Student ID")
        self.rank_tree.heading("Name", text="Name")
        self.rank_tree.heading("Roll No", text="Roll No")
        self.rank_tree.heading("Total Marks", text="Total Marks")
        self.rank_tree.heading("Average", text="Average")
        self.rank_tree.heading("Semester", text="Semester")
        
        # Set column widths
        self.rank_tree.column("Rank", width=50)
        self.rank_tree.column("Student ID", width=100)
        self.rank_tree.column("Name", width=150)
        self.rank_tree.column("Roll No", width=100)
        self.rank_tree.column("Total Marks", width=100)
        self.rank_tree.column("Average", width=100)
        self.rank_tree.column("Semester", width=100)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.rank_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.rank_tree.xview)
        
        # Configure scrollbars
        self.rank_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack scrollbars and treeview
        self.rank_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Bind filter events
        self.rank_semester_filter.trace('w', self.update_subject_filter)
        self.rank_semester_filter.trace('w', self.update_rank_list)
        self.rank_subject_filter.trace('w', self.update_rank_list)
        self.rank_exam_type_filter.trace('w', self.update_rank_list)
        
        # Load initial rank list
        self.update_rank_list()

    def update_rank_list(self, *args):
        """Update the rank list based on selected filters"""
        # Clear existing items
        for item in self.rank_tree.get_children():
            self.rank_tree.delete(item)
            
        try:
            # Connect to database
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # Build query based on filters
            query = """
            WITH StudentTotals AS (
                SELECT 
                    r.std_id,
                    u.full_name,
                    r.roll_no,
                    r.semester,
                    r.subject,
                    r.marks,
                    COUNT(*) OVER (PARTITION BY r.std_id, r.semester) as subject_count
                FROM results r
                JOIN users u ON r.std_id = u.username
                WHERE 1=1
            """
            
            params = []
            
            if self.rank_semester_filter.get() != "All":
                query += " AND r.semester = ?"
                params.append(int(self.rank_semester_filter.get()))
                
            if self.rank_subject_filter.get() != "All":
                query += " AND r.subject = ?"
                params.append(self.rank_subject_filter.get())
                
            if self.rank_exam_type_filter.get() != "All":
                query += " AND r.exam_type = ?"
                params.append(self.rank_exam_type_filter.get())
                
            query += """
            )
            SELECT 
                ROW_NUMBER() OVER (ORDER BY SUM(marks) DESC) as rank,
                std_id,
                full_name,
                roll_no,
                SUM(marks) as total_marks,
                ROUND(AVG(CAST(marks AS FLOAT)), 1) as average_marks,
                semester
            FROM StudentTotals
            GROUP BY std_id, full_name, roll_no, semester
            HAVING COUNT(DISTINCT subject) = (
                SELECT COUNT(DISTINCT subject) 
                FROM results 
                WHERE semester = StudentTotals.semester
            )
            ORDER BY total_marks DESC
            """
            
            cursor.execute(query, params)
            results = cursor.fetchall()
            
            # Insert into treeview
            for result in results:
                self.rank_tree.insert('', 'end', values=result)
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()

    def show_rank_list(self):
        """Show the rank list tab"""
        self.clear_content()
        self.setup_rank_list_tab()
        # Update button states
        self.add_result_btn.state(['!disabled'])
        self.view_result_btn.state(['!disabled'])
        self.rank_list_btn.state(['!disabled'])

    def export_rank_list_csv(self):
        """Export rank list to CSV file"""
        if not self.rank_tree.get_children():
            messagebox.showinfo("Export", "No data to export!")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.csv',
                filetypes=[("CSV files", '*.csv')],
                title="Export Rank List"
            )
            
            if filename:
                with open(filename, 'w', newline='') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # Write headers
                    headers = [self.rank_tree.heading(col)['text'] for col in self.rank_tree['columns']]
                    writer.writerow(headers)
                    
                    # Write filter information
                    writer.writerow(['Filters'])
                    writer.writerow(['Semester', self.rank_semester_filter.get()])
                    writer.writerow(['Subject', self.rank_subject_filter.get()])
                    writer.writerow(['Exam Type', self.rank_exam_type_filter.get()])
                    writer.writerow([])  # Empty row for separation
                    
                    # Write data
                    for item in self.rank_tree.get_children():
                        row = self.rank_tree.item(item)['values']
                        writer.writerow(row)
                        
                messagebox.showinfo("Export Successful", f"Rank list exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")

    def export_rank_list_pdf(self):
        """Export rank list to PDF file"""
        if not self.rank_tree.get_children():
            messagebox.showinfo("Export", "No data to export!")
            return
            
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension='.pdf',
                filetypes=[("PDF files", '*.pdf')],
                title="Export Rank List"
            )
            
            if filename:
                # Create PDF document
                doc = SimpleDocTemplate(filename, pagesize=letter)
                elements = []
                
                # Add title
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=getSampleStyleSheet()['Title'],
                    fontSize=16,
                    spaceAfter=30
                )
                elements.append(Paragraph("Rank List Report", title_style))
                
                # Add filter information
                filter_style = ParagraphStyle(
                    'FilterStyle',
                    parent=getSampleStyleSheet()['Normal'],
                    fontSize=10,
                    spaceAfter=10
                )
                elements.append(Paragraph(f"Semester: {self.rank_semester_filter.get()}", filter_style))
                elements.append(Paragraph(f"Subject: {self.rank_subject_filter.get()}", filter_style))
                elements.append(Paragraph(f"Exam Type: {self.rank_exam_type_filter.get()}", filter_style))
                elements.append(Spacer(1, 20))
                
                # Create table data
                data = [[self.rank_tree.heading(col)['text'] for col in self.rank_tree['columns']]]
                for item in self.rank_tree.get_children():
                    data.append(self.rank_tree.item(item)['values'])
                
                # Create table
                table = Table(data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 10),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table)
                
                # Build PDF
                doc.build(elements)
                messagebox.showinfo("Export Successful", f"Rank list exported to {filename}")
                
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred while exporting: {str(e)}")

    def fetch_student_details(self, event=None):
        """Fetch student details when student ID is entered"""
        std_id = self.std_id_entry.get().strip()
        if not std_id:
            return
            
        try:
            # Connect to database
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # First try to get details from users table
            cursor.execute('''
            SELECT full_name FROM users 
            WHERE username = ? AND role = 'student'
            ''', (std_id,))
            user_result = cursor.fetchone()
            
            if user_result:
                # Get the most recent roll number from results
                cursor.execute('''
                SELECT roll_no FROM results 
                WHERE std_id = ? 
                ORDER BY added_at DESC LIMIT 1
                ''', (std_id,))
                roll_result = cursor.fetchone()
                
                # Update the entry fields
                self.name_entry.delete(0, tk.END)
                self.name_entry.insert(0, user_result[0])
                
                if roll_result:
                    self.roll_no_entry.delete(0, tk.END)
                    self.roll_no_entry.insert(0, roll_result[0])
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to fetch student details: {str(e)}")
        finally:
            if conn:
                conn.close()

# To test the dashboard independently
if __name__ == "__main__":
    root = tk.Tk()
    app = TeacherDashboard(root, "admin")
    root.mainloop()