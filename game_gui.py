import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import cv2
from image_processor import ImageProcessor


class SpotDifferenceGame:
    """
    Main GUI class for the Spot The Difference Game.
    """

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
        self.score = 0
        self.time_left = 300  # 5 minutes
        self.difficulty = 'medium'
        self.timer_running = False

        self.create_widgets()

    def create_widgets(self):
        """
        Creates all GUI widgets.
        """
        # Title
        title_label = tk.Label(self.root, text="Spot The Difference Game", font=("Arial", 16))
        title_label.pack(pady=10)

        # Instructions
        instructions_label = tk.Label(self.root, text="Click on the differences in the right image.", font=("Arial", 12))
        instructions_label.pack(pady=5)

        # Top frame for buttons and difficulty
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)

        load_button = tk.Button(top_frame, text="Load Image", command=self.load_image, width=15)
        load_button.grid(row=0, column=0, padx=5)

        reveal_button = tk.Button(top_frame, text="Reveal Answers", command=self.reveal_answers, width=15)
        reveal_button.grid(row=0, column=1, padx=5)

        # Difficulty selection
        difficulty_label = tk.Label(top_frame, text="Difficulty:")
        difficulty_label.grid(row=0, column=2, padx=5)

        self.difficulty_var = tk.StringVar(value='medium')
        easy_radio = tk.Radiobutton(top_frame, text="Easy", variable=self.difficulty_var, value='easy')
        easy_radio.grid(row=0, column=3, padx=5)
        medium_radio = tk.Radiobutton(top_frame, text="Medium", variable=self.difficulty_var, value='medium')
        medium_radio.grid(row=0, column=4, padx=5)
        hard_radio = tk.Radiobutton(top_frame, text="Hard", variable=self.difficulty_var, value='hard')
        hard_radio.grid(row=0, column=5, padx=5)

        # Labels for remaining, mistakes, score, timer
        self.remaining_label = tk.Label(self.root, text="Remaining Differences: 5", font=("Arial", 14))
        self.remaining_label.pack()

        self.mistake_label = tk.Label(self.root, text="Mistakes: 0 / 3", font=("Arial", 14))
        self.mistake_label.pack()

        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 14))
        self.score_label.pack()

        self.timer_label = tk.Label(self.root, text="Time: 5:00", font=("Arial", 14))
        self.timer_label.pack()

        # Image frame
        image_frame = tk.Frame(self.root)
        image_frame.pack(pady=10)

        # Left canvas
        left_label = tk.Label(image_frame, text="Original Image")
        left_label.grid(row=0, column=0)
        self.left_canvas = tk.Canvas(image_frame, width=500, height=500, highlightthickness=2, highlightbackground="black")
        self.left_canvas.grid(row=1, column=0, padx=10)

        # Right canvas
        right_label = tk.Label(image_frame, text="Modified Image")
        right_label.grid(row=0, column=1)
        self.right_canvas = tk.Canvas(image_frame, width=500, height=500, highlightthickness=2, highlightbackground="black", cursor="crosshair")
        self.right_canvas.grid(row=1, column=1, padx=10)
        self.right_canvas.bind("<Button-1>", self.check_click)

    def load_image(self):
        """
        Loads an image, resizes maintaining aspect ratio, creates differences.
        """
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.png *.bmp")])
        if not file_path:
            return

        image = cv2.imread(file_path)
        if image is None:
            messagebox.showerror("Error", "Image could not be loaded.")
            return

        # Resize maintaining aspect ratio
        height, width = image.shape[:2]
        max_size = 500
        if width > height:
            new_width = max_size
            new_height = int(height * max_size / width)
        else:
            new_height = max_size
            new_width = int(width * max_size / height)
        image = cv2.resize(image, (new_width, new_height))

        # Pad to 500x500
        pad_x = (500 - new_width) // 2
        pad_y = (500 - new_height) // 2
        padded = cv2.copyMakeBorder(image, pad_y, 500 - new_height - pad_y, pad_x, 500 - new_width - pad_x, cv2.BORDER_CONSTANT, value=[0, 0, 0])

        self.original_image = padded.copy()
        self.difficulty = self.difficulty_var.get()
        self.modified_image = self.processor.create_differences(padded, self.difficulty)

        self.display_original = self.original_image.copy()
        self.display_modified = self.modified_image.copy()

        self.remaining = 5
        self.mistakes = 0
        self.score = 0
        self.time_left = 300
        self.timer_running = True

        self.update_labels()
        self.show_images()
        self.update_timer()

    def convert_image(self, image):
        """
        Converts OpenCV image to Tkinter PhotoImage.
        """
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        pil_image = Image.fromarray(rgb)
        return ImageTk.PhotoImage(pil_image)

    def show_images(self):
        """
        Displays the images on the canvases.
        """
        self.tk_original = self.convert_image(self.display_original)
        self.tk_modified = self.convert_image(self.display_modified)
        self.left_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_original)
        self.right_canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_modified)

    def update_labels(self):
        """
        Updates all label texts.
        """
        self.remaining_label.config(text=f"Remaining Differences: {self.remaining}")
        self.mistake_label.config(text=f"Mistakes: {self.mistakes} / 3")
        self.score_label.config(text=f"Score: {self.score}")

    def update_timer(self):
        """
        Updates the timer every second.
        """
        if self.timer_running and self.time_left > 0:
            self.time_left -= 1
            min_ = self.time_left // 60
            sec = self.time_left % 60
            self.timer_label.config(text=f"Time: {min_}:{sec:02d}")
            self.root.after(1000, self.update_timer)
        elif self.time_left == 0:
            self.game_over("Time's up!")

    def check_click(self, event):
        """
        Handles click on the right canvas.
        """
        if self.mistakes >= 3 or self.remaining == 0:
            return

        found = False
        for diff in self.processor.differences:
            if not diff.found and diff.contains(event.x, event.y):
                diff.found = True
                found = True
                self.remaining -= 1
                self.score += 10
                # Draw red circle on both
                center_x = diff.x + diff.w // 2
                center_y = diff.y + diff.h // 2
                radius = min(diff.w, diff.h) // 2 - 5
                cv2.circle(self.display_original, (center_x, center_y), radius, (0, 0, 255), 3)
                cv2.circle(self.display_modified, (center_x, center_y), radius, (0, 0, 255), 3)
                break

        if not found:
            self.mistakes += 1
            self.score -= 5
            if self.mistakes >= 3:
                self.game_over("You made 3 mistakes.")

        self.update_labels()
        self.show_images()

        if self.remaining == 0:
            self.win()

    def win(self):
        """
        Handles winning the game.
        """
        self.timer_running = False
        bonus = self.time_left // 10
        self.score += bonus
        self.update_labels()
        messagebox.showinfo("Congratulations", f"You found all differences!\nScore: {self.score}\nTime: {300 - self.time_left}s\nMistakes: {self.mistakes}\nFound: 5")

    def game_over(self, reason):
        """
        Handles game over.
        """
        self.timer_running = False
        self.reveal_answers()
        self.remaining = 0
        self.update_labels()
        found = 5 - self.remaining  # but since remaining=0, found=5? Wait, no, remaining is set to 0 after reveal, but actually found is the ones found before.
        # Wait, better to count found
        found = sum(1 for diff in self.processor.differences if diff.found)
        messagebox.showinfo("Game Over", f"{reason}\nScore: {self.score}\nTime: {300 - self.time_left}s\nMistakes: {self.mistakes}\nFound: {found}")

    def reveal_answers(self):
        """
        Reveals all remaining differences.
        """
        for diff in self.processor.differences:
            if not diff.found:
                center_x = diff.x + diff.w // 2
                center_y = diff.y + diff.h // 2
                radius = min(diff.w, diff.h) // 2 - 5
                cv2.circle(self.display_original, (center_x, center_y), radius, (255, 0, 0), 3)
                cv2.circle(self.display_modified, (center_x, center_y), radius, (255, 0, 0), 3)
        self.show_images()