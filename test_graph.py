import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

def create_test_graph():
    # Create a sample window
    root = tk.Tk()
    root.title("Test Graph")
    root.geometry("800x600")
    
    # Create a frame to hold the graph
    frame = ttk.Frame(root)
    frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    # Set seaborn style
    sns.set_style("whitegrid")
    sns.set_context("notebook", font_scale=1.2)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(8, 5))
    
    # Sample data
    subjects = ['MATHS4', 'OS', 'CNND', 'COA', 'AT']
    marks = [85, 92, 78, 88, 95]
    
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
    plt.xticks(rotation=30, ha='right')
    
    # Adjust layout to prevent label cutoff
    plt.tight_layout()
    
    # Create canvas and add to frame
    canvas = FigureCanvasTkAgg(fig, master=frame)
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
    
    # Add a status label
    status_label = ttk.Label(root, text="Graph created successfully with seaborn")
    status_label.pack(pady=10)
    
    root.mainloop()

if __name__ == "__main__":
    create_test_graph() 