from os                 import listdir
from random             import choice

class MusicPlayer:
    def __init__(self, music_folder):
        self.music_folder = music_folder
        self.songs = []
        self.current_index = 0
        self.shuffle_mode = False
        self.load_songs()

    def load_songs(self):
        self.songs = [f for f in listdir(self.music_folder) if f.endswith(('.mp3', '.m4a', '.wav'))]

    def previous_song(self):
        # Retroceder al índice anterior, volviendo al final si estamos en la primera canción
        self.current_index = (self.current_index - 1) % len(self.songs)
        return self.songs[self.current_index]

    def next_song(self):
        if self.shuffle_mode:
            self.current_index = choice([i for i in range(len(self.songs)) if i != self.current_index])
        else:
            self.current_index = (self.current_index + 1) % len(self.songs)

        return self.songs[self.current_index]

    def select_song(self, song_number):
        if song_number < 1 or song_number > len(self.songs):
            raise ValueError("Número de canción no válido.")
        self.current_index = song_number - 1
        return self.songs[self.current_index]

    def toggle_shuffle(self):
        self.shuffle_mode = not self.shuffle_mode