import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class StudentDashboard:
    # Valid subjects list to match teacher dashboard
    SUBJECTS = ["MATHS4", "OS", "CNND", "COA", "AT", "MATHS3", "DSA", "PCPF", "DBMS", "PCOM"]
    
    def __init__(self, root, username):
        self.root = root
        self.username = username
        self.root.title(f"Student Dashboard - {username}")
        self.root.geometry("1000x700")
        self.root.configure(bg="#e3f2fd")  # Light blue background
        
        # Initialize database connection
        self.conn = sqlite3.connect('student_results.db')
        self.cursor = self.conn.cursor()
        
        # Initialize student data
        self.student_profile = None
        self.student_results = []
        
        # Load data and setup UI
        self.load_student_data()
        self.setup_ui()
        
        # Check if using default password and show warning
        self.check_default_password()
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
    
    def setup_ui(self):
        # Header Frame
        header_frame = tk.Frame(self.root, bg="#2196f3", height=80)
        header_frame.pack(fill=tk.X)
        
        # Title
        tk.Label(header_frame, text="Student Dashboard", font=("Arial", 20, "bold"), 
                bg="#2196f3", fg="white").pack(side=tk.LEFT, padx=20, pady=20)
        
        # Right side container
        right_container = tk.Frame(header_frame, bg="#2196f3")
        right_container.pack(side=tk.RIGHT, padx=20)
        
        # Configure logout button style
        style = ttk.Style()
        style.configure("Logout.TButton", 
                       font=("Arial", 11, "bold"),
                       foreground="#e53935",  # Red text for logout
                       padding=8)
        
        # Logout Button
        logout_btn = ttk.Button(
            right_container, 
            text="Logout", 
            command=self.logout,
            style="Logout.TButton"
        )
        logout_btn.pack(side=tk.RIGHT, padx=10)
        
        # Student Name
        if self.student_profile:
            tk.Label(right_container, text=f"Welcome, {self.student_profile[3]}", 
                    font=("Arial", 14), bg="#2196f3", fg="white").pack(side=tk.RIGHT, padx=10)
        
        # Create a navigation frame with gradient effect
        self.nav_frame = tk.Frame(self.root, bg="#bbdefb", height=60)
        self.nav_frame.pack(fill=tk.X)
        
        # Add a separator for visual appeal
        separator = ttk.Separator(self.root, orient="horizontal")
        separator.pack(fill=tk.X, padx=5)
        
        # Create and configure button styles
        style = ttk.Style()
        
        # Configure the active button style (selected section)
        style.configure(
            "Active.Nav.TButton",
            font=("Arial", 12, "bold"),
            foreground="#1565c0",  # Dark blue text
            background="#e3f2fd",  # Light blue background
            padding=10,
            borderwidth=0
        )
        
        # Configure the normal button style
        style.configure(
            "Nav.TButton",
            font=("Arial", 12),
            foreground="#424242",  # Dark gray text
            background="#bbdefb",  # Light blue background
            padding=10,
            borderwidth=0
        )
        
        # Navigation Buttons container
        btn_frame = tk.Frame(self.nav_frame, bg="#bbdefb")
        btn_frame.pack(anchor="center", pady=10)
        
        # Navigation Buttons
        self.results_btn = ttk.Button(
            btn_frame, text="My Results", style="Nav.TButton",
            command=self.show_results
        )
        self.results_btn.pack(side=tk.LEFT, padx=15)
        
        self.analytics_btn = ttk.Button(
            btn_frame, text="Progress Analytics", style="Nav.TButton",
            command=self.show_analytics
        )
        self.analytics_btn.pack(side=tk.LEFT, padx=15)
        
        self.profile_btn = ttk.Button(
            btn_frame, text="My Profile", style="Nav.TButton",
            command=self.show_profile
        )
        self.profile_btn.pack(side=tk.LEFT, padx=15)
        
        # Create a main content frame with border
        self.content_frame = tk.Frame(self.root, bg="white", bd=1, relief=tk.SOLID)
        self.content_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create frames for different sections (initially hidden)
        self.results_frame = tk.Frame(self.content_frame, bg="white")
        self.analytics_frame = tk.Frame(self.content_frame, bg="white")
        self.profile_frame = tk.Frame(self.content_frame, bg="white")
        
        # Setup each section
        self.setup_results_tab()
        self.setup_analytics_tab()
        self.setup_profile_tab()
        
        # Show results by default
        self.show_results()
    
    def setup_results_tab(self):
        # Add a title for this section
        title_frame = tk.Frame(self.results_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        ttk.Label(title_frame, text="My Academic Results", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Separator(title_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Create a frame for the treeview and scrollbar
        tree_frame = ttk.Frame(self.results_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Treeview for results with style
        style = ttk.Style()
        style.configure("Treeview", font=("Arial", 10))
        style.configure("Treeview.Heading", font=("Arial", 11, "bold"))
        
        self.results_tree = ttk.Treeview(tree_frame, 
                                       columns=("Subject", "Marks", "Grade", "Added By", "Date"),
                                       show="headings",
                                       height=15)
        
        # Configure columns
        self.results_tree.heading("Subject", text="Subject")
        self.results_tree.heading("Marks", text="Marks")
        self.results_tree.heading("Grade", text="Grade")
        self.results_tree.heading("Added By", text="Added By")
        self.results_tree.heading("Date", text="Date Added")
        
        # Set column widths
        self.results_tree.column("Subject", width=150)
        self.results_tree.column("Marks", width=100)
        self.results_tree.column("Grade", width=100)
        self.results_tree.column("Added By", width=150)
        self.results_tree.column("Date", width=150)
        
        # Add scrollbars
        y_scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.results_tree.yview)
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.results_tree.xview)
        
        # Configure scrollbars
        self.results_tree.configure(yscrollcommand=y_scrollbar.set, xscrollcommand=x_scrollbar.set)
        
        # Pack everything
        self.results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add a status bar
        status_frame = tk.Frame(self.results_frame, bg="#f5f5f5", height=30)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        
        # Load data
        self.load_results()
    
    def setup_analytics_tab(self):
        # Add a title for this section
        title_frame = ttk.Frame(self.analytics_frame)
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        ttk.Label(title_frame, text="Academic Performance Analytics", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Separator(title_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Create main container for analytics
        analytics_container = ttk.Frame(self.analytics_frame)
        analytics_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)
        
        # Create a frame for rank position (vertical)
        rank_frame = ttk.LabelFrame(analytics_container, text="Your Position", padding=15)
        rank_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 15))
        
        # Create a frame for rank details
        rank_details = ttk.Frame(rank_frame)
        rank_details.pack(fill=tk.Y, expand=True)
        
        # Add rank position label with large font
        self.rank_position_label = ttk.Label(rank_details, text="", font=("Arial", 36, "bold"))
        self.rank_position_label.pack(pady=20)
        
        # Add total students label
        self.total_students_label = ttk.Label(rank_details, text="", font=("Arial", 12))
        self.total_students_label.pack(pady=5)
        
        # Add percentile label
        self.percentile_label = ttk.Label(rank_details, text="", font=("Arial", 12))
        self.percentile_label.pack(pady=5)
        
        # Create a frame for the graph (right side)
        self.graph_frame = ttk.Frame(analytics_container)
        self.graph_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Generate initial chart and rank position
        self.create_bar_graph()
        self.update_rank_position()
    
    def setup_profile_tab(self):
        # Add a title for this section
        title_frame = tk.Frame(self.profile_frame, bg="white")
        title_frame.pack(fill=tk.X, padx=15, pady=(15, 5))
        ttk.Label(title_frame, text="My Profile Information", font=("Arial", 16, "bold")).pack(anchor="w")
        ttk.Separator(title_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Profile container
        profile_container = tk.Frame(self.profile_frame, bg="white")
        profile_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Left side - Profile picture placeholder
        img_frame = tk.Frame(profile_container, bg="#e0e0e0", width=200, height=200)
        img_frame.pack(side=tk.LEFT, padx=(0, 20))
        img_frame.pack_propagate(False)  # Prevent frame from shrinking
        
        # Profile icon placeholder
        tk.Label(img_frame, text="👤", font=("Arial", 80), bg="#e0e0e0").pack(expand=True)
        
        # Right side - Profile info
        info_container = tk.Frame(profile_container, bg="white")
        info_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Profile info frame with some padding and style
        info_frame = ttk.LabelFrame(info_container, text="Student Information", padding=20)
        info_frame.pack(fill=tk.X)
        
        # Profile info labels with values
        if self.student_profile:
            info_data = [
                ("Full Name:", self.student_profile[3]),
                ("Username/ID:", self.student_profile[1]),
                ("Roll No:", self.roll_no if self.roll_no else "Not assigned")
            ]
            
            for i, (label, value) in enumerate(info_data):
                ttk.Label(info_frame, text=label, font=("Arial", 12, "bold")).grid(row=i, column=0, sticky="e", padx=5, pady=8)
                ttk.Label(info_frame, text=value, font=("Arial", 12)).grid(row=i, column=1, sticky="w", padx=5, pady=8)
        
        # Buttons container
        button_container = tk.Frame(info_container, bg="white")
        button_container.pack(fill=tk.X, pady=20)
        
        # Add change password button
        style = ttk.Style()
        style.configure("Profile.TButton", 
                      font=("Arial", 11), 
                      foreground="#4CAF50",  # Green text for profile buttons
                      padding=8)
        
        ttk.Button(button_container, text="Change Password", style="Profile.TButton", 
                 command=self.show_change_password).pack(side=tk.LEFT, padx=5)
    
    def load_student_data(self):
        """Load all student data from database"""
        try:
            # Get student profile
            self.cursor.execute('''
            SELECT id, username, password, full_name 
            FROM users 
            WHERE username=? AND role='student'
            ''', (self.username,))
            self.student_profile = self.cursor.fetchone()
            
            if not self.student_profile:
                messagebox.showerror("Error", "Student profile not found!")
                self.root.destroy()
                return
            
            # Get student results
            self.cursor.execute('''
            SELECT subject, marks, added_by, added_at, roll_no 
            FROM results 
            WHERE std_id=?
            ORDER BY subject
            ''', (self.username,))
            self.student_results = self.cursor.fetchall()
            
            # Get roll number from results (if any)
            self.roll_no = None
            if self.student_results:
                self.roll_no = self.student_results[0][4]  # Get roll_no from the first result
            
            # If there are no results, show a message
            if not self.student_results:
                messagebox.showinfo("Information", "No results found. Please check with your teacher.")
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to load student data: {str(e)}")
            self.root.destroy()
    
    def load_results(self):
        """Load results into Treeview"""
        # Clear existing items
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)
        
        # Insert new data
        for subject, marks, added_by, added_at, _ in self.student_results:
            grade = self.calculate_grade(marks)
            self.results_tree.insert("", tk.END, values=(subject, marks, grade, added_by, added_at))
    
    def calculate_grade(self, marks):
        """Calculate grade based on marks"""
        if marks >= 90: return "A+"
        elif marks >= 80: return "A"
        elif marks >= 70: return "B"
        elif marks >= 60: return "C"
        elif marks >= 50: return "D"
        else: return "F"
    
    def update_chart(self):
        """Update the progress chart"""
        # Clear previous chart
        for widget in self.chart_frame.winfo_children():
            widget.destroy()
        
        if not self.student_results:
            ttk.Label(self.chart_frame, text="No results available for visualization").pack()
            return
        
        # Prepare data
        subjects = [row[0] for row in self.student_results]
        marks = [row[1] for row in self.student_results]
        
        # Create figure
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(subjects, marks, color='#2196f3')
        
        # Customize chart
        ax.set_title('Subject-wise Performance')
        ax.set_ylabel('Marks')
        ax.set_ylim(0, 100)
        plt.xticks(rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}',
                    ha='center', va='bottom')
        
        # Adjust layout
        plt.tight_layout()
        
        # Embed in Tkinter
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    def load_profile(self):
        """Load profile data into labels"""
        if self.student_profile:
            self.profile_data["Full Name:"].config(text=self.student_profile[3])
            self.profile_data["Username:"].config(text=self.student_profile[1])
            self.profile_data["Roll No:"].config(text=self.roll_no)
    
    def show_change_password(self):
        # Create change password dialog
        dialog = tk.Toplevel(self.root)
        dialog.title("Change Password")
        dialog.geometry("500x450")  # Make dialog larger
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.configure(bg="white")
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (
            self.root.winfo_rootx() + self.root.winfo_width()//2 - 250,
            self.root.winfo_rooty() + self.root.winfo_height()//2 - 225
        ))
        
        # Make sure dialog has a minimum size
        dialog.minsize(500, 450)
        
        # Dialog header
        header_frame = tk.Frame(dialog, bg="#2196f3", height=60)
        header_frame.pack(fill=tk.X)
        
        tk.Label(
            header_frame, 
            text="Change Your Password", 
            font=("Arial", 14, "bold"), 
            bg="#2196f3", 
            fg="white"
        ).pack(pady=15)
        
        # Create and pack widgets
        content_frame = tk.Frame(dialog, bg="white", padx=30, pady=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Style for entries
        style = ttk.Style()
        style.configure("Password.TEntry", font=("Arial", 12))
        
        # Current password
        ttk.Label(content_frame, text="Current Password:", font=("Arial", 12)).pack(fill=tk.X, pady=(15, 5), anchor="w")
        current_pwd_frame = tk.Frame(content_frame, bg="white")
        current_pwd_frame.pack(fill=tk.X, pady=5)
        
        current_pwd = ttk.Entry(current_pwd_frame, show="•", style="Password.TEntry")
        current_pwd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Add show/hide toggle for current password
        ttk.Button(current_pwd_frame, text="👁", width=3, style="Eye.TButton",
                 command=lambda: toggle_password_visibility(current_pwd)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # New password
        ttk.Label(content_frame, text="New Password:", font=("Arial", 12)).pack(fill=tk.X, pady=(15, 5), anchor="w")
        new_pwd_frame = tk.Frame(content_frame, bg="white")
        new_pwd_frame.pack(fill=tk.X, pady=5)
        
        new_pwd = ttk.Entry(new_pwd_frame, show="•", style="Password.TEntry")
        new_pwd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        # Confirm password
        ttk.Label(content_frame, text="Confirm Password:", font=("Arial", 12)).pack(fill=tk.X, pady=(15, 5), anchor="w")
        confirm_pwd_frame = tk.Frame(content_frame, bg="white")
        confirm_pwd_frame.pack(fill=tk.X, pady=5)
        
        confirm_pwd = ttk.Entry(confirm_pwd_frame, show="•", style="Password.TEntry")
        confirm_pwd.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=5)
        
        def toggle_password_visibility(entry):
            current_show = entry['show']
            entry['show'] = '' if current_show else '•'
        
        # Show/Hide password buttons
        style.configure("Eye.TButton", 
                      font=("Arial", 10),
                      foreground="#757575")  # Gray text for eye button
        
        ttk.Button(new_pwd_frame, text="👁", width=3, style="Eye.TButton",
                 command=lambda: toggle_password_visibility(new_pwd)).pack(side=tk.RIGHT, padx=(5, 0))
        
        ttk.Button(confirm_pwd_frame, text="👁", width=3, style="Eye.TButton",
                 command=lambda: toggle_password_visibility(confirm_pwd)).pack(side=tk.RIGHT, padx=(5, 0))
        
        # Create fixed bottom section to ensure buttons are always visible
        bottom_frame = tk.Frame(dialog, bg="white", height=120, padx=30, pady=20)
        bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)
        
        # Add a separator before buttons
        ttk.Separator(bottom_frame, orient="horizontal").pack(fill=tk.X, pady=5)
        
        # Button styles
        style.configure("Primary.TButton", 
                      font=("Arial", 12, "bold"), 
                      foreground="#0D47A1",  # Dark blue text for primary button
                      padding=10)
        
        style.configure("Secondary.TButton", 
                      font=("Arial", 12), 
                      foreground="#455A64",  # Dark slate gray for secondary button
                      padding=10)
        
        # Buttons - Make them more prominent
        button_frame = tk.Frame(bottom_frame, bg="white")
        button_frame.pack(fill=tk.X, pady=10)
        
        # Save button - using a colored frame to make it stand out
        save_btn_frame = tk.Frame(button_frame, bg="#1976D2", padx=2, pady=2)
        save_btn_frame.pack(side=tk.LEFT, padx=5)
        
        def change_password():
            current = current_pwd.get()
            new = new_pwd.get()
            confirm = confirm_pwd.get()
            
            # Validation
            if not current or not new or not confirm:
                messagebox.showerror("Error", "All fields are required!")
                return
                
            if new != confirm:
                messagebox.showerror("Error", "New passwords do not match!")
                return
            
            if len(new) < 6:
                messagebox.showerror("Error", "Password must be at least 6 characters long!")
                return
            
            try:
                # First verify current password
                self.cursor.execute('''
                SELECT id FROM users 
                WHERE username = ? AND password = ? AND role = 'student'
                ''', (self.username, current))
                
                user = self.cursor.fetchone()
                if not user:
                    messagebox.showerror("Error", "Current password is incorrect!")
                    return
                
                # Update password
                self.cursor.execute('''
                UPDATE users 
                SET password = ? 
                WHERE username = ? AND role = 'student'
                ''', (new, self.username))
                
                self.conn.commit()
                messagebox.showinfo("Success", "Password changed successfully!")
                dialog.destroy()
                
            except sqlite3.Error as e:
                self.conn.rollback()
                messagebox.showerror("Database Error", f"Failed to change password: {str(e)}")
        
        # Use a regular tk.Button instead of ttk.Button for better color control
        save_btn = tk.Button(
            save_btn_frame,
            text="Save Changes",
            font=("Arial", 12, "bold"),
            bg="#2196F3",  # Blue background
            fg="white",    # White text
            activebackground="#1976D2",  # Darker blue when clicked
            activeforeground="white",
            command=change_password,
            width=15,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=8
        )
        save_btn.pack(padx=1, pady=1)
        
        # Cancel button - also make it a regular button for consistency
        tk.Button(
            button_frame, 
            text="Cancel", 
            font=("Arial", 12),
            bg="#E0E0E0",  # Light gray background
            fg="#333333",  # Dark gray text
            activebackground="#BDBDBD",  # Darker gray when clicked
            command=dialog.destroy,
            width=12,
            cursor="hand2",
            relief=tk.RAISED,
            bd=1,
            padx=10,
            pady=8
        ).pack(side=tk.LEFT, padx=5)
        
        # Add status text at bottom
        tk.Label(
            bottom_frame,
            text="Click 'Save Changes' to update your password",
            font=("Arial", 9),
            fg="#666666",
            bg="white"
        ).pack(side=tk.BOTTOM, pady=5)
    
    def on_closing(self):
        """Handle window closing"""
        if hasattr(self, 'conn'):
            self.conn.close()
        self.root.destroy()

    def create_bar_graph(self):
        # Clear previous graph
        for widget in self.graph_frame.winfo_children():
            widget.destroy()
        
        # Set seaborn style
        sns.set_style("whitegrid")
        sns.set_context("notebook", font_scale=1.2)
        
        # Create figure
        fig, ax = plt.subplots(figsize=(12, 8))  # Larger figure for more subjects
        
        # Get data from student_results
        if not self.student_results:
            ttk.Label(self.graph_frame, text="No results available for visualization", 
                     font=("Arial", 14)).pack(pady=50)
            return
        
        # Extract data - create a dictionary to store the highest mark for each subject
        # since a student might have multiple exams for the same subject
        subjects_data = {}
        for subject, mark, _, _, _ in self.student_results:
            # Keep the highest mark for each subject
            if subject not in subjects_data or mark > subjects_data[subject]:
                subjects_data[subject] = mark
        
        # Convert to lists for plotting, maintaining consistent order
        subjects = []
        marks = []
        for subject in self.SUBJECTS:
            if subject in subjects_data:
                subjects.append(subject)
                marks.append(subjects_data[subject])
        
        if not subjects:
            ttk.Label(self.graph_frame, text="No results available for visualization", 
                     font=("Arial", 14)).pack(pady=50)
            return
        
        # Create a color palette
        palette = sns.color_palette("husl", len(subjects))
        
        # Create bars with seaborn
        bars = sns.barplot(x=subjects, y=marks, palette=palette, ax=ax)
        
        # Add value labels on top of bars
        for i, bar in enumerate(ax.patches):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                   f'{int(height)}%',
                   ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Customize the graph
        ax.set_title('Subject-wise Performance', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Subjects', fontsize=14, fontweight='bold', labelpad=10)
        ax.set_ylabel('Marks (%)', fontsize=14, fontweight='bold', labelpad=10)
        
        # Set y-axis limits with some padding
        ax.set_ylim(0, min(105, max(marks) + 10))
        
        # Remove top and right spines
        sns.despine()
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45, ha='right')
        
        # Add a subtle background color
        fig.patch.set_facecolor('#f8f9fa')
        
        # Adjust layout to prevent label cutoff
        plt.tight_layout()
        
        # Create canvas and add to frame
        canvas = FigureCanvasTkAgg(fig, master=self.graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Add a legend with color squares in a scrollable frame if many subjects
        legend_frame = ttk.Frame(self.graph_frame)
        legend_frame.pack(fill=tk.X, padx=10, pady=(5, 10))
        
        # Create legend items
        for i, subject in enumerate(subjects):
            legend_item = ttk.Frame(legend_frame)
            legend_item.pack(side=tk.LEFT, padx=10)
            
            # Color square
            color = palette[i]
            color_hex = "#{:02x}{:02x}{:02x}".format(
                int(color[0]*255), int(color[1]*255), int(color[2]*255)
            )
            
            color_square = tk.Canvas(legend_item, width=15, height=15, bg=color_hex)
            color_square.pack(side=tk.LEFT, padx=(0, 5))
            
            # Subject label
            ttk.Label(legend_item, text=subject, font=('Helvetica', 10)).pack(side=tk.LEFT)

    def show_results(self):
        # Update button states
        self.results_btn.configure(state="disabled", style="Active.Nav.TButton")
        self.analytics_btn.configure(state="normal", style="Nav.TButton")
        self.profile_btn.configure(state="normal", style="Nav.TButton")
        
        # Hide other frames and show results frame
        self.analytics_frame.pack_forget()
        self.profile_frame.pack_forget()
        self.results_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_analytics(self):
        # Update button states
        self.results_btn.configure(state="normal", style="Nav.TButton")
        self.analytics_btn.configure(state="disabled", style="Active.Nav.TButton")
        self.profile_btn.configure(state="normal", style="Nav.TButton")
        
        # Hide other frames and show analytics frame
        self.results_frame.pack_forget()
        self.profile_frame.pack_forget()
        self.analytics_frame.pack(fill=tk.BOTH, expand=True)
        
    def show_profile(self):
        # Update button states
        self.results_btn.configure(state="normal", style="Nav.TButton")
        self.analytics_btn.configure(state="normal", style="Nav.TButton")
        self.profile_btn.configure(state="disabled", style="Active.Nav.TButton")
        
        # Hide other frames and show profile frame
        self.results_frame.pack_forget()
        self.analytics_frame.pack_forget()
        self.profile_frame.pack(fill=tk.BOTH, expand=True)

    def logout(self):
        """Logout and return to login screen"""
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            # Close database connection
            if hasattr(self, 'conn'):
                self.conn.close()
            
            # Destroy current window
            self.root.destroy()
            
            # Open login window again
            from login import LoginWindow
            login_root = tk.Tk()
            LoginWindow(login_root)
            login_root.mainloop()

    def check_default_password(self):
        """Check if user is using default password and show warning"""
        if not self.student_profile:
            return
            
        # Get current password
        current_password = self.student_profile[2]
        
        # Check if it's the default password
        if current_password == "student123":
            # Wait a short time before showing dialog to ensure UI is ready
            self.root.after(1000, self.show_password_warning)
    
    def show_password_warning(self):
        """Show warning dialog for default password"""
        result = messagebox.askquestion(
            "Security Warning",
            "You are using the default password which is not secure.\n\n"
            "Would you like to change your password now?",
            icon="warning"
        )
        
        if result == "yes":
            self.show_change_password()

    def update_rank_position(self):
        """Update the student's rank position in the class"""
        try:
            # Connect to database
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # Get the student's current semester
            cursor.execute("""
                SELECT DISTINCT semester 
                FROM results 
                WHERE std_id = ? 
                ORDER BY semester DESC 
                LIMIT 1
            """, (self.username,))
            current_semester = cursor.fetchone()
            
            if not current_semester:
                self.rank_position_label.config(text="No Data Available")
                self.total_students_label.config(text="")
                self.percentile_label.config(text="")
                return
                
            current_semester = current_semester[0]
            
            # Calculate total marks for each student in the current semester
            query = """
            WITH StudentTotals AS (
                SELECT 
                    r.std_id,
                    SUM(r.marks) as total_marks,
                    COUNT(*) as subject_count
                FROM results r
                WHERE r.semester = ?
                GROUP BY r.std_id
                HAVING subject_count = (
                    SELECT COUNT(DISTINCT subject) 
                    FROM results 
                    WHERE semester = ?
                )
            )
            SELECT 
                std_id,
                total_marks,
                ROW_NUMBER() OVER (ORDER BY total_marks DESC) as rank,
                COUNT(*) OVER () as total_students
            FROM StudentTotals
            """
            
            cursor.execute(query, (current_semester, current_semester))
            results = cursor.fetchall()
            
            # Find student's rank
            student_rank = None
            total_students = 0
            
            for std_id, total_marks, rank, total in results:
                if std_id == self.username:
                    student_rank = rank
                    total_students = total
                    break
            
            if student_rank is not None:
                # Update rank position label
                self.rank_position_label.config(
                    text=f"#{student_rank}",
                    foreground="#2196F3"  # Blue color for rank
                )
                
                # Update total students label
                self.total_students_label.config(
                    text=f"Out of {total_students} Students"
                )
                
                # Calculate and update percentile
                percentile = ((total_students - student_rank + 1) / total_students) * 100
                self.percentile_label.config(
                    text=f"Top {percentile:.1f}% of the Class"
                )
            else:
                self.rank_position_label.config(text="No Data Available")
                self.total_students_label.config(text="")
                self.percentile_label.config(text="")
                
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"An error occurred: {str(e)}")
        finally:
            if conn:
                conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = StudentDashboard(root, "alice")  # Test with sample student
    root.mainloop()