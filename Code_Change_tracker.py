import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
import difflib

class CodeTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Code Change Tracker")
        self.root.geometry("1200x600")  # Initial size of the window

        self.original_text = None
        self.modified_text = None
        self.file_path = None

        # Setup UI
        self.create_widgets()

    def create_widgets(self):
        # Frame for buttons
        frame = tk.Frame(self.root)
        frame.pack(pady=5)

        open_button = tk.Button(frame, text="Open Text File", command=self.open_file)
        open_button.pack(side=tk.LEFT, padx=5)

        apply_changes_button = tk.Button(frame, text="Apply Changes", command=self.apply_changes)
        apply_changes_button.pack(side=tk.LEFT, padx=5)

        # Main frame with grid for resizable text areas and copy buttons
        text_frame = tk.Frame(self.root)
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Original text widget
        self.original_text_widget = scrolledtext.ScrolledText(
            text_frame, wrap=tk.NONE, undo=True, width=60, height=30
        )
        self.original_text_widget.grid(row=0, column=0, sticky="nsew")
        self.original_text_widget.bind("<<Modified>>", self.on_text_change)
        self.original_text_widget.bind("<Button-3>", self.show_context_menu)  # Right-click for context menu

        # Copy Original Code Button
        copy_original_button = tk.Button(text_frame, text="Copy Original Code", command=self.copy_original_code)
        copy_original_button.grid(row=1, column=0, pady=5)

        # Modified text widget
        self.modified_text_widget = scrolledtext.ScrolledText(
            text_frame, wrap=tk.NONE, undo=True, width=60, height=30
        )
        self.modified_text_widget.grid(row=0, column=1, sticky="nsew")
        self.modified_text_widget.bind("<<Modified>>", self.on_text_change)
        self.modified_text_widget.bind("<Button-3>", self.show_context_menu)  # Right-click for context menu

        # Copy Modified Code Button
        copy_modified_button = tk.Button(text_frame, text="Copy Modified Code", command=self.copy_modified_code)
        copy_modified_button.grid(row=1, column=1, pady=5)

        # Grid configuration to make text areas resizable
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=1)
        text_frame.grid_rowconfigure(0, weight=1)

        # Context menu for copying
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Copy Line", command=self.copy_line)
        self.context_menu.add_command(label="Copy Entire Text", command=self.copy_text_area)

    def open_file(self):
        # Open file dialog to select a text file of various types
        self.file_path = filedialog.askopenfilename(
            title="Open Text File",
            filetypes=[
                ("Python files", "*.py"),
                ("HTML files", "*.html"),
                ("JavaScript files", "*.js"),
                ("Java files", "*.java"),
                ("Text files", "*.txt"),
                ("All files", "*.*")
            ]
        )
        if not self.file_path:
            return

        try:
            with open(self.file_path, 'r', encoding='utf-8') as file:
                self.original_text = file.readlines()
            
            # Initialize modified text with original content
            self.modified_text = self.original_text.copy()

            self.display_texts()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {e}")

    def display_texts(self):
        # Display original text
        self.original_text_widget.configure(state='normal')
        self.original_text_widget.delete(1.0, tk.END)
        self.original_text_widget.insert(tk.END, ''.join(self.original_text))
        self.original_text_widget.edit_modified(False)  # Reset modified state

        # Display modified text
        self.modified_text_widget.configure(state='normal')
        self.modified_text_widget.delete(1.0, tk.END)
        self.modified_text_widget.insert(tk.END, ''.join(self.modified_text))
        self.modified_text_widget.edit_modified(False)  # Reset modified state

        # Highlight any changes initially
        self.highlight_changes()

    def on_text_change(self, event):
        # Determine which text widget was edited
        widget = event.widget
        widget.edit_modified(False)

        # Update the internal content of each text area
        if widget == self.original_text_widget:
            self.original_text = self.original_text_widget.get("1.0", tk.END).splitlines(keepends=True)
        elif widget == self.modified_text_widget:
            self.modified_text = self.modified_text_widget.get("1.0", tk.END).splitlines(keepends=True)

        # Highlight changes in both text widgets
        self.highlight_changes()

    def highlight_changes(self):
        # Clear previous highlights in both text areas
        self.original_text_widget.tag_remove("highlight", "1.0", tk.END)
        self.modified_text_widget.tag_remove("highlight", "1.0", tk.END)

        # Compare original and modified text line by line
        diff = difflib.ndiff(self.original_text, self.modified_text)

        # Highlight the differences in both text widgets
        for i, line in enumerate(diff):
            line_type = line[0]  # This could be ' ', '-', or '+'
            content = line[2:]   # The actual line content

            if line_type == '-':  # Line present in original but not in modified
                line_num = self.original_text.index(content) + 1
                line_index = f"{line_num}.0"
                self.original_text_widget.tag_add("highlight", line_index, f"{line_index} lineend")
            
            elif line_type == '+':  # Line present in modified but not in original
                line_num = self.modified_text.index(content) + 1
                line_index = f"{line_num}.0"
                self.modified_text_widget.tag_add("highlight", line_index, f"{line_index} lineend")

        # Configure highlight colors
        self.original_text_widget.tag_config("highlight", background="lightcoral")
        self.modified_text_widget.tag_config("highlight", background="lightgreen")

    def apply_changes(self):
        # Ask for confirmation before applying changes
        if messagebox.askyesno("Confirm", "Are you sure you want to apply these changes?"):
            with open(self.file_path, 'w', encoding='utf-8') as file:
                file.writelines(self.modified_text)
            messagebox.showinfo("Success", "Changes applied successfully.")
            self.original_text = self.modified_text.copy()
            self.display_texts()

    def show_context_menu(self, event):
        # Track the text widget and position of right-click
        self.context_menu_text_widget = event.widget
        self.context_menu_line_index = self.context_menu_text_widget.index("@%d,%d linestart" % (event.x, event.y))
        self.context_menu.post(event.x_root, event.y_root)

    def copy_line(self):
        # Copy the specific line where right-click occurred
        line_text = self.context_menu_text_widget.get(self.context_menu_line_index, f"{self.context_menu_line_index} lineend")
        self.root.clipboard_clear()
        self.root.clipboard_append(line_text)
        messagebox.showinfo("Copy Line", "Line copied to clipboard.")

    def copy_text_area(self):
        # Copy the entire content of the selected text widget
        content = self.context_menu_text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        messagebox.showinfo("Copy Entire Text", "Text area copied to clipboard.")

    def copy_original_code(self):
        # Copy all content from the original text area
        original_content = self.original_text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(original_content)
        messagebox.showinfo("Copy Original Code", "Original code copied to clipboard.")

    def copy_modified_code(self):
        # Copy all content from the modified text area
        modified_content = self.modified_text_widget.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(modified_content)
        messagebox.showinfo("Copy Modified Code", "Modified code copied to clipboard.")

# Initialize Tkinter app
root = tk.Tk()
app = CodeTrackerApp(root)
root.mainloop()
