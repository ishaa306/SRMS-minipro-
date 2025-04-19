import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import sqlite3
import os
from database import initialize_database
from teacher_dashboard import TeacherDashboard
from student_dashboard import StudentDashboard

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Result System - Login")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        
        # Initialize database
        initialize_database()
        
        # Background Image (optional)
        if os.path.exists("login_bg.jpg"):
            image = Image.open("login_bg.jpg")
            image = image.resize((500, 400), Image.Resampling.LANCZOS)
            self.bg_image = ImageTk.PhotoImage(image)
            bg_label = tk.Label(root, image=self.bg_image)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        
        # Login Frame
        login_frame = tk.Frame(root, bg="#E6E6FA", padx=20, pady=20)  # Light purple background
        login_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
        
        # Title
        tk.Label(login_frame, text="Student Result System", font=("Arial", 16, "bold"), 
                bg="#E6E6FA", fg="#4B0082").grid(row=0, column=0, columnspan=2, pady=10)
        
        # Username
        tk.Label(login_frame, text="Username:", bg="#E6E6FA", fg="#4B0082").grid(row=1, column=0, sticky="w", pady=5)
        self.username_entry = ttk.Entry(login_frame)
        self.username_entry.grid(row=1, column=1, pady=5)
        
        # Password
        tk.Label(login_frame, text="Password:", bg="#E6E6FA", fg="#4B0082").grid(row=2, column=0, sticky="w", pady=5)
        self.password_entry = ttk.Entry(login_frame, show="*")
        self.password_entry.grid(row=2, column=1, pady=5)
        
        # Show Password Checkbox
        self.show_password_var = tk.BooleanVar()
        ttk.Checkbutton(login_frame, text="Show Password", variable=self.show_password_var, 
                       command=self.toggle_password_visibility).grid(row=3, column=1, sticky="w", pady=5)
        
        # Role Selection
        tk.Label(login_frame, text="Role:", bg="#E6E6FA", fg="#4B0082").grid(row=4, column=0, sticky="w", pady=5)
        self.role_var = tk.StringVar(value="student")
        ttk.Radiobutton(login_frame, text="Student", variable=self.role_var, value="student").grid(row=4, column=1, sticky="w")
        ttk.Radiobutton(login_frame, text="Teacher", variable=self.role_var, value="teacher").grid(row=5, column=1, sticky="w")
        
        # Login Button
        style = ttk.Style()
        style.configure("Custom.TButton", background="#FF69B4", foreground="#4B0082")
        ttk.Button(login_frame, text="Login", command=self.authenticate, style="Custom.TButton").grid(row=6, column=0, columnspan=2, pady=10)
        
       
    
    def authenticate(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_var.get()
        
        if not username or not password:
            messagebox.showerror("Error", "Please enter both username and password!")
            return
        
        try:
            conn = sqlite3.connect('student_results.db')
            cursor = conn.cursor()
            
            # First check if user exists with given role
            cursor.execute('''
            SELECT id, username, password, role, full_name 
            FROM users 
            WHERE username = ? AND role = ?
            ''', (username, role))
            
            user = cursor.fetchone()
            
            if not user:
                messagebox.showerror("Error", f"No {role} account found with this username!")
                conn.close()
                return
            
            # Then verify password
            if user[2] != password:  # user[2] is password
                messagebox.showerror("Error", "Incorrect password!")
                conn.close()
                return
            
            # If we get here, authentication is successful
            messagebox.showinfo("Success", f"Welcome, {user[4]}!")
            conn.close()
            
            self.root.destroy()  # Close login window
            
            # Open appropriate dashboard
            root = tk.Tk()
            if role == "teacher":
                app = TeacherDashboard(root, username)
            else:
                app = StudentDashboard(root, username)
            root.mainloop()
            
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Failed to authenticate: {str(e)}")
            if 'conn' in locals():
                conn.close()
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            if 'conn' in locals():
                conn.close()

    def toggle_password_visibility(self):
        if self.show_password_var.get():
            self.password_entry.config(show="")
        else:
            self.password_entry.config(show="*")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()