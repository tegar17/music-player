import tkinter as tk
import customtkinter as ctk
import pygame
from PIL import Image, ImageTk
from threading import Thread
import time
import os

class MusicPlayer:
    def __init__(self, root):
        self.root = root
        self.root.title("Music Player")
        self.root.geometry("360x620")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Initialize pygame mixer
        pygame.mixer.init()
        
        # Song and cover lists
        self.list_of_songs = ["audio/lofi.mp3", "audio/sad_guitar.mp3"]
        self.list_of_covers = ["image/pic 2.jpeg", "image/guitar.jpg"]
        self.current_index = 0
        
        # Control flags
        self.is_playing = False
        self.is_running = True
        self.progress_thread = None
        
        # UI Components
        self.album_cover_label = None
        self.song_name_label = None
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize all UI components"""
        # Play button
        self.play_button = ctk.CTkButton(
            master=self.root, 
            text="Play", 
            command=self.toggle_play,
            width=100
        )
        self.play_button.place(relx=0.5, rely=0.7, anchor=tk.CENTER)
        
        # Skip forward button
        self.skip_button_f = ctk.CTkButton(
            master=self.root, 
            text="►", 
            command=self.skip_forward, 
            width=50
        )
        self.skip_button_f.place(relx=0.72, rely=0.7, anchor=tk.CENTER)
        
        # Skip backward button
        self.skip_button_b = ctk.CTkButton(
            master=self.root, 
            text="◄", 
            command=self.skip_backward, 
            width=50
        )
        self.skip_button_b.place(relx=0.28, rely=0.7, anchor=tk.CENTER)
        
        # Volume slider
        self.slider = ctk.CTkSlider(
            master=self.root, 
            from_=0, 
            to=1, 
            command=self.set_volume, 
            width=210
        )
        self.slider.set(0.5)
        self.slider.place(relx=0.5, rely=0.79, anchor=tk.CENTER)
        
        # Progress bar
        self.progress_bar = ctk.CTkProgressBar(
            master=self.root, 
            progress_color='#32a85a', 
            width=250
        )
        self.progress_bar.set(0)
        self.progress_bar.place(relx=0.51, rely=0.6, anchor=tk.CENTER)
    
    def get_album_cover(self, song_index):
        """Display album cover and song name"""
        try:
            # Load and resize image
            image = Image.open(self.list_of_covers[song_index])
            image = image.resize((340, 400))
            photo = ImageTk.PhotoImage(image)
            
            # Remove old label if exists
            if self.album_cover_label:
                self.album_cover_label.destroy()
            
            # Create new label
            self.album_cover_label = tk.Label(self.root, image=photo, bg='#222222', highlightbackground="#ffffff", highlightthickness=3)
            self.album_cover_label.image = photo  # Keep reference
            self.album_cover_label.place(relx=0.13, rely=0.05)
            
            # Display song name
            song_name = os.path.basename(self.list_of_songs[song_index])[:-4]
            
            if self.song_name_label:
                self.song_name_label.destroy()
            
            self.song_name_label = tk.Label(
                self.root, 
                text=song_name, 
                bg='#222222', 
                fg='white',
                font=('Arial', 18)
            )
            self.song_name_label.place(relx=0.5, rely=0.64, anchor=tk.CENTER)
        
        except Exception as e:
            print(f"Error loading album cover: {e}")
    
    def update_progress(self):
        """Update progress bar in a separate thread"""
        try:
            # Get song length
            sound = pygame.mixer.Sound(self.list_of_songs[self.current_index])
            song_length = sound.get_length()
            
            start_time = time.time()
            
            while self.is_running and self.is_playing:
                elapsed_time = time.time() - start_time
                
                if elapsed_time >= song_length:
                    self.progress_bar.set(1.0)
                    break
                
                progress = elapsed_time / song_length
                self.progress_bar.set(progress)
                time.sleep(0.1)
            
        except Exception as e:
            print(f"Error updating progress: {e}")
    
    def play_music(self):
        """Play the current song"""
        try:
            # Ensure index is within bounds
            if self.current_index >= len(self.list_of_songs):
                self.current_index = 0
            
            # Load and play music
            pygame.mixer.music.load(self.list_of_songs[self.current_index])
            pygame.mixer.music.play(loops=0)
            pygame.mixer.music.set_volume(self.slider.get())
            
            # Update UI
            self.get_album_cover(self.current_index)
            self.is_playing = True
            self.play_button.configure(text="Pause")
            
            # Start progress thread
            if self.progress_thread and self.progress_thread.is_alive():
                self.is_playing = False
                self.progress_thread.join(timeout=1)
            
            self.is_playing = True
            self.progress_thread = Thread(target=self.update_progress, daemon=True)
            self.progress_thread.start()
            
        except Exception as e:
            print(f"Error playing music: {e}")
    
    def toggle_play(self):
        """Toggle between play and pause"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            self.play_button.configure(text="Play")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
                self.is_playing = True
                self.play_button.configure(text="Pause")
            else:
                self.play_music()
    
    def skip_forward(self):
        """Skip to next song"""
        pygame.mixer.music.stop()
        self.current_index += 1
        if self.current_index >= len(self.list_of_songs):
            self.current_index = 0
        self.play_music()
    
    def skip_backward(self):
        """Skip to previous song"""
        pygame.mixer.music.stop()
        self.current_index -= 1
        if self.current_index < 0:
            self.current_index = len(self.list_of_songs) - 1
        self.play_music()
    
    def set_volume(self, value):
        """Set music volume"""
        pygame.mixer.music.set_volume(value)
    
    def on_closing(self):
        """Properly close the application"""
        self.is_running = False
        self.is_playing = False
        
        # Stop music
        pygame.mixer.music.stop()
        
        # Wait for thread to finish
        if self.progress_thread and self.progress_thread.is_alive():
            self.progress_thread.join(timeout=1)
        
        # Quit pygame
        pygame.mixer.quit()
        
        # Destroy window
        self.root.destroy()

def main():
    # Set appearance
    ctk.set_appearance_mode("System")
    ctk.set_default_color_theme("blue")
    
    # Create root window
    root = ctk.CTk()
    
    # Create music player
    app = MusicPlayer(root)
    
    # Run application
    root.mainloop()

if __name__ == "__main__":
    main()