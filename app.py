import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from tkinter import ttk
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import io

class PDFReaderAnnotator:
    def __init__(self, master):
        self.master = master
        self.master.title("Simple PDF Reader")
        self.master.geometry("800x600")

        self.pdf_file_path = None
        self.page_images = []
        self.current_page = 0
        self.zoom_factor = 1.0
        self.page_rotation = 0  # Track rotation
        self.annotations = []
        self.highlights = []
        self.text_annotations = []

        self.canvas = tk.Canvas(self.master, bg="white")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # Scroll & Drag Variables
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<MouseWheel>", self.zoom_with_scroll)

        self.start_x = 0
        self.start_y = 0

        self.create_menu()
        self.create_controls()
        self.load_pdf_button()

    def create_menu(self):
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)
        
        file_menu = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF", command=self.load_pdf)
        file_menu.add_command(label="Save Annotations", command=self.save_annotations)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.master.quit)

    def create_controls(self):
        control_frame = ttk.Frame(self.master)
        control_frame.pack(side="bottom", fill="x", pady=10)

        self.prev_page_button = ttk.Button(control_frame, text="Previous", command=self.prev_page)
        self.prev_page_button.pack(side="left", padx=10)

        self.next_page_button = ttk.Button(control_frame, text="Next", command=self.next_page)
        self.next_page_button.pack(side="left", padx=10)

        self.rotate_button = ttk.Button(control_frame, text="Rotate", command=self.rotate_page)
        self.rotate_button.pack(side="left", padx=10)

        self.zoom_slider = ttk.Scale(control_frame, from_=0.5, to=2.0, orient="horizontal", command=self.on_zoom_slider_change)
        self.zoom_slider.set(self.zoom_factor)
        self.zoom_slider.pack(side="left", fill="x", expand=True)

    def load_pdf_button(self):
        load_button = ttk.Button(self.master, text="Load PDF", command=self.load_pdf)
        load_button.pack(side="top", pady=10)

    def load_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        self.pdf_file_path = file_path
        self.page_images = self.extract_pdf_images()
        self.current_page = 0
        self.page_rotation = 0  # Reset rotation
        if self.page_images:
            self.display_page()
        else:
            messagebox.showerror("Error", "Failed to load PDF.")

    def extract_pdf_images(self):
        doc = fitz.open(self.pdf_file_path)
        page_images = []
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # Higher resolution
            img = Image.open(io.BytesIO(pix.tobytes("ppm")))
            page_images.append(img)
        return page_images

    def display_page(self):
        if not self.page_images:
            return
        img = self.page_images[self.current_page]

        # Apply rotation
        rotated_img = img.rotate(self.page_rotation, expand=True)

        # Apply zoom
        new_size = (int(rotated_img.width * self.zoom_factor), int(rotated_img.height * self.zoom_factor))
        resized_img = rotated_img.resize(new_size)

        self.tk_image = ImageTk.PhotoImage(resized_img)
        self.canvas.delete("all")  # Clear previous canvas items
        self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def rotate_page(self):
        if not self.page_images:
            return
        self.page_rotation = (self.page_rotation + 90) % 360  # Rotate in 90-degree increments
        self.display_page()

    def on_zoom_slider_change(self, value):
        self.zoom_factor = float(value)
        self.display_page()

    def zoom_with_scroll(self, event):
        if event.delta > 0:
            self.zoom_factor = min(self.zoom_factor + 0.1, 2.0)
        else:
            self.zoom_factor = max(self.zoom_factor - 0.1, 0.5)
        self.zoom_slider.set(self.zoom_factor)
        self.display_page()

    def start_drag(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def drag(self, event):
        delta_x = event.x - self.start_x
        delta_y = event.y - self.start_y
        self.canvas.move("all", delta_x, delta_y)
        self.start_x = event.x
        self.start_y = event.y

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.page_rotation = 0  # Reset rotation on page change
            self.display_page()

    def next_page(self):
        if self.current_page < len(self.page_images) - 1:
            self.current_page += 1
            self.page_rotation = 0  # Reset rotation on page change
            self.display_page()

    def save_annotations(self):
        with open('annotations.txt', 'w') as f:
            for annotation in self.text_annotations:
                f.write(f"{annotation}\n")
        messagebox.showinfo("Saved", "Annotations saved!")

if __name__ == "__main__":
    root = tk.Tk()
    app = PDFReaderAnnotator(root)
    root.mainloop()
