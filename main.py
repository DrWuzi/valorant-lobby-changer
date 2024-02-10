import os
import json
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
import shutil
import cv2
from PIL import Image, ImageTk


class VideoPlayerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Player")

        # Center the window on the screen
        window_width = 420
        window_height = 350
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_coordinate = (screen_width - window_width) // 2
        y_coordinate = (screen_height - window_height) // 2
        root.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # Initialize variables
        self.video_files = []
        self.current_index = 0

        # Check if the 'videos' directory exists
        if not os.path.exists('videos'):
            os.makedirs('videos')

        # Initialize the video files array with files from the 'videos' directory
        self.video_files = [os.path.join('videos', f) for f in os.listdir('videos') if f.endswith(('.mp4', '.avi', '.mov', '.mkv'))]

        # Load the last selected video index from the config file
        self.config_file_path = os.path.join(os.getcwd(), 'config.json')
        self.load_last_selected_video()

        # Create GUI elements
        self.label_video_name = tk.Label(self.root, text="")
        self.label_video_name.grid(row=0, column=0, columnspan=3, pady=5, sticky="ew")

        self.button_prev_video = tk.Button(self.root, text="Previous Video", command=self.prev_video)
        self.button_prev_video.grid(row=1, column=0, padx=10, pady=5, sticky="ew")

        self.button_select_video = tk.Button(self.root, text="Select Video", command=self.select_video)
        self.button_select_video.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        self.button_next_video = tk.Button(self.root, text="Next Video", command=self.next_video)
        self.button_next_video.grid(row=1, column=2, padx=10, pady=5, sticky="ew")

        self.video_label = tk.Label(self.root)
        self.video_label.grid(row=2, column=0, columnspan=3, pady=10, sticky="nsew")

        self.button_apply = tk.Button(self.root, text="Apply", command=self.apply_changes)
        self.button_apply.grid(row=3, column=0, columnspan=3, pady=5, sticky="ew")

        # Set row and column weights to expand the grid
        self.root.grid_rowconfigure(2, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_columnconfigure(1, weight=1)
        self.root.grid_columnconfigure(2, weight=1)

        # Display the currently selected video
        self.display_video()

    def save_last_selected_video(self):
        try:
            # Load existing configuration data if the file exists
            config_data = {}
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as config_file:
                    config_data = json.load(config_file)

            # Update the configuration with the new selected video
            config_data["last_selected_video"] = self.current_index
            config_data["last_selected_video_path"] = self.video_files[self.current_index]

            # Save the updated configuration to the file
            with open(self.config_file_path, 'w') as config_file:
                json.dump(config_data, config_file, indent=4)
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while saving last selected video: {str(e)}")

    def load_last_selected_video(self):
        try:
            # Load the last selected video index and path from the config file
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as config_file:
                    config_data = json.load(config_file)
                    if 'last_selected_video' in config_data and 'last_selected_video_path' in config_data:
                        last_selected_video_index = config_data['last_selected_video']
                        last_selected_video_path = config_data['last_selected_video_path']
                        # Check if the last selected video path exists in the current video files
                        if last_selected_video_path in self.video_files:
                            self.current_index = self.video_files.index(last_selected_video_path)
                        else:
                            # If the last selected video path doesn't exist, select the next video
                            if self.video_files:
                                self.current_index = min(last_selected_video_index, len(self.video_files) - 1)
                            else:
                                self.current_index = 0
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while loading last selected video: {str(e)}")

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4")])
        if file_path:
            # Copy the selected video file to the 'videos' directory
            destination = os.path.join('videos', os.path.basename(file_path))
            shutil.copy(file_path, destination)

            # Add the copied file to the video files array
            self.video_files.append(destination)

            # Display the newly selected video
            self.current_index = len(self.video_files) - 1
            self.display_video()

            # Save the current selected video
            self.save_last_selected_video()

    def display_video(self):
        if self.video_files:
            # Update the label to display the selected video name
            video_name = os.path.basename(self.video_files[self.current_index])
            self.label_video_name.config(text=video_name)

            # Load the selected video file
            current_video = self.video_files[self.current_index]
            cap = cv2.VideoCapture(current_video)

            # Read the first frame of the video
            ret, frame = cap.read()

            if ret:
                # Convert the frame to RGB format
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                # Resize the frame to fit the display area
                image = Image.fromarray(frame_rgb)
                image.thumbnail((400, 300))

                # Convert the image to a format compatible with tkinter
                photo = ImageTk.PhotoImage(image=image)

                # Update the label to display the new image
                self.video_label.config(image=photo)
                self.video_label.image = photo

            # Release the video capture object
            cap.release()

    def prev_video(self):
        if self.video_files:
            self.current_index = (self.current_index - 1) % len(self.video_files)
            self.display_video()
            self.save_last_selected_video()  # Save the current selected video

    def next_video(self):
        if self.video_files:
            self.current_index = (self.current_index + 1) % len(self.video_files)
            self.display_video()
            self.save_last_selected_video()  # Save the current selected video

    def apply_changes(self):
        # Check if there's a selected video
        if self.video_files:
            # Get the selected video file path
            selected_video = self.video_files[self.current_index]

            # Get the target directory from the config file
            valorant_directory = self.load_or_select_valorant_directory()

            try:
                # Check if the target directory exists
                if valorant_directory and os.path.exists(valorant_directory):
                    # Check if the selected video file exists
                    if os.path.exists(selected_video):
                        # Get the list of .mp4 files in the target directory
                        mp4_files = [f for f in os.listdir(valorant_directory) if f.endswith('.mp4')]

                        # Copy the selected video to the target directory and replace all .mp4 files
                        for mp4_file in mp4_files:
                            shutil.copy(selected_video, os.path.join(valorant_directory, mp4_file))

                        # Inform the user about the successful operation
                        messagebox.showinfo("Success", "Changes applied successfully.")
                    else:
                        # Inform the user if the selected video file does not exist
                        messagebox.showerror("Error", "Selected video file does not exist.")
                else:
                    # Inform the user if the target directory is not specified or does not exist
                    messagebox.showerror("Error", "Valorant directory not specified or does not exist.")
            except Exception as e:
                # Inform the user about the error
                messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def load_or_select_valorant_directory(self):
        try:
            # Load the Valorant directory from the config file if available
            config_data = {}
            if os.path.exists(self.config_file_path):
                with open(self.config_file_path, 'r') as config_file:
                    config_data = json.load(config_file)
            valorant_directory = config_data.get('valorant_directory')

            # If Valorant directory is not available in the config, prompt the user to select it
            if not valorant_directory or not os.path.exists(valorant_directory):
                valorant_directory = filedialog.askdirectory(title="Select Valorant Directory")
                if valorant_directory:
                    # Normalize the path and split it
                    valorant_directory_parts = os.path.normpath(valorant_directory).split(os.sep)
                    # Find the index of the last occurrence of 'Riot Games' in the path
                    if 'Riot Games' in valorant_directory_parts and 'VALORANT' in valorant_directory_parts:
                        valorant_index = valorant_directory_parts.index('VALORANT')
                        valorant_directory = "\\".join(valorant_directory_parts[:valorant_index+1]) + "\\live\\ShooterGame\\Content\\Movies\\Menu"
                    else:
                        messagebox.showerror("Error", "Valorant directory must contain 'Riot Games' and 'VALORANT' directory.")
                        return None
                    # Update the config with the selected directory
                    config_data['valorant_directory'] = valorant_directory
                    with open(self.config_file_path, 'w') as config_file:
                        json.dump(config_data, config_file, indent=4)
            return valorant_directory
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while selecting Valorant directory: {str(e)}")
            return None


def main():
    root = tk.Tk()
    app = VideoPlayerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
