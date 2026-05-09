import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
import random


# ---------------- DIFFERENCE CLASS ---------------- #

class Difference:

    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.found = False

    def contains(self, click_x, click_y):

        return (
            self.x <= click_x <= self.x + self.w
            and
            self.y <= click_y <= self.y + self.h
        )


# ---------------- IMAGE PROCESSOR ---------------- #

class ImageProcessor:

    def __init__(self):
        self.differences = []

    def create_differences(self, image):

        modified = image.copy()

        height, width, _ = image.shape

        self.differences = []

        while len(self.differences) < 5:

            diff_width = random.randint(40, 80)
            diff_height = random.randint(40, 80)

            x = random.randint(0, width - diff_width - 1)
            y = random.randint(0, height - diff_height - 1)

            overlap = False

            # Prevent overlapping differences
            for diff in self.differences:

                if (
                    x < diff.x + diff.w
                    and x + diff_width > diff.x
                    and y < diff.y + diff.h
                    and y + diff_height > diff.y
                ):
                    overlap = True
                    break

            if overlap:
                continue

            region = modified[y:y + diff_height, x:x + diff_width]

            effect = random.choice(["blur", "brightness", "color"])

            if effect == "blur":

                region = cv2.GaussianBlur(region, (15, 15), 0)

            elif effect == "brightness":

                region = cv2.convertScaleAbs(region, alpha=1.2, beta=30)

            elif effect == "color":

                region[:, :, 1] = 255

            modified[y:y + diff_height, x:x + diff_width] = region

            self.differences.append(
                Difference(x, y, diff_width, diff_height)
            )

        return modified


# ---------------- GAME GUI ---------------- #

class SpotDifferenceGame:

    def __init__(self, root):

        self.root = root
        self.root.title("Spot The Difference Game")

        self.processor = ImageProcessor()

        self.original_image = None
        self.modified_image = None

        self.display_original = None
        self.display_modified = None

        self.tk_original = None
        self.tk_modified = None

        self.remaining = 5
        self.mistakes = 0

        self.create_widgets()

    # ---------- CREATE GUI ---------- #

    def create_widgets(self):

        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        load_button = tk.Button(
            top_frame,
            text="Load Image",
            command=self.load_image,
            width=15
        )

        load_button.grid(row=0, column=0, padx=5)

        reveal_button = tk.Button(
            top_frame,
            text="Reveal Answers",
            command=self.reveal_answers,
            width=15
        )

        reveal_button.grid(row=0, column=1, padx=5)

        self.remaining_label = tk.Label(
            self.root,
            text="Remaining Differences: 5",
            font=("Arial", 14)
        )

        self.remaining_label.pack()

        self.mistake_label = tk.Label(
            self.root,
            text="Mistakes: 0 / 3",
            font=("Arial", 14)
        )

        self.mistake_label.pack()

        image_frame = tk.Frame(self.root)
        image_frame.pack(pady=10)

        self.left_canvas = tk.Canvas(
            image_frame,
            width=500,
            height=500
        )

        self.left_canvas.grid(row=0, column=0, padx=10)

        self.right_canvas = tk.Canvas(
            image_frame,
            width=500,
            height=500
        )

        self.right_canvas.grid(row=0, column=1, padx=10)

        self.right_canvas.bind("<Button-1>", self.check_click)

    # ---------- LOAD IMAGE ---------- #

    def load_image(self):

        file_path = filedialog.askopenfilename(
            filetypes=[("Image Files", "*.jpg *.png *.bmp")]
        )

        if not file_path:
            return

        image = cv2.imread(file_path)

        if image is None:

            messagebox.showerror(
                "Error",
                "Image could not be loaded."
            )

            return

        image = cv2.resize(image, (500, 500))

        self.original_image = image.copy()

        self.modified_image = self.processor.create_differences(image)

        self.display_original = self.original_image.copy()
        self.display_modified = self.modified_image.copy()

        self.remaining = 5
        self.mistakes = 0

        self.update_labels()

        self.show_images()

    # ---------- CONVERT IMAGE ---------- #

    def convert_image(self, image):

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        pil_image = Image.fromarray(rgb)

        return ImageTk.PhotoImage(pil_image)

    # ---------- SHOW IMAGES ---------- #

    def show_images(self):

        self.tk_original = self.convert_image(self.display_original)

        self.tk_modified = self.convert_image(self.display_modified)

        self.left_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.tk_original
        )

        self.right_canvas.create_image(
            0,
            0,
            anchor=tk.NW,
            image=self.tk_modified
        )

    # ---------- UPDATE LABELS ---------- #

    def update_labels(self):

        self.remaining_label.config(
            text=f"Remaining Differences: {self.remaining}"
        )

        self.mistake_label.config(
            text=f"Mistakes: {self.mistakes} / 3"
        )

    # ---------- CHECK CLICK ---------- #

    def check_click(self, event):

        found = False

        for diff in self.processor.differences:

            if not diff.found and diff.contains(event.x, event.y):

                diff.found = True

                found = True

                self.remaining -= 1

                cv2.rectangle(
                    self.display_original,
                    (diff.x, diff.y),
                    (diff.x + diff.w, diff.y + diff.h),
                    (0, 0, 255),
                    3
                )

                cv2.rectangle(
                    self.display_modified,
                    (diff.x, diff.y),
                    (diff.x + diff.w, diff.y + diff.h),
                    (0, 0, 255),
                    3
                )

                break

        if not found:

            self.mistakes += 1

            if self.mistakes >= 3:

                messagebox.showinfo(
                    "Game Over",
                    "You made 3 mistakes."
                )

        self.update_labels()

        self.show_images()

        if self.remaining == 0:

            messagebox.showinfo(
                "Congratulations",
                "You found all differences!"
            )

    # ---------- REVEAL ANSWERS ---------- #

    def reveal_answers(self):

        for diff in self.processor.differences:

            if not diff.found:

                cv2.rectangle(
                    self.display_original,
                    (diff.x, diff.y),
                    (diff.x + diff.w, diff.y + diff.h),
                    (255, 0, 0),
                    3
                )

                cv2.rectangle(
                    self.display_modified,
                    (diff.x, diff.y),
                    (diff.x + diff.w, diff.y + diff.h),
                    (255, 0, 0),
                    3
                )

        self.show_images()

        messagebox.showinfo(
            "Reveal",
            "All differences are shown."
        )


# ---------------- MAIN PROGRAM ---------------- #

root = tk.Tk()

game = SpotDifferenceGame(root)

root.mainloop()