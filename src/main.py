from flask              import Flask, jsonify, render_template, request, send_file, redirect, url_for, session
from werkzeug.utils     import secure_filename
from os.path            import join
from time               import time
from sys                import argv, exit
from os                 import urandom

from .UserManager        import UserManager
from .MusicPlayer        import MusicPlayer


class StreamingApp:
    def __init__(self, music_folder, port=80):
        self.music_player = MusicPlayer(music_folder)
        self.user_manager = UserManager()
        self.port = port
        self.app = Flask(__name__, template_folder=join("..", "templates"), static_folder=join("..", "static"))
        self.app.secret_key = urandom(512)
        self.app.config['UPLOAD_FOLDER'] = music_folder
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/')
        def index():
            if 'user_id' not in session:
                return redirect(url_for('login'))

            if not self.music_player.songs:
                return render_template('no_index.html')

            song_table = "<ul style='list-style: none; padding: 0;'>"
            for i, song in enumerate(self.music_player.songs):
                style = f"padding: 10px; margin: 5px; background-color: {'#4caf50' if i == self.music_player.current_index else '#f9f9f9'}; color: {'#fff' if i == self.music_player.current_index else '#333'}; border-radius: 8px; text-align: left; cursor: pointer;"
                song_table += f"<li style='{style}' onclick='selectSong({i + 1})'>{i + 1}. {song}</li>"
            song_table += "</ul>"

            return render_template('index.html',
                song_table=song_table,
                song_now=self.music_player.songs[self.music_player.current_index],
                play_url=f"/play?{int(time())}"
            )

        @self.app.route('/login', methods=['GET', 'POST'])
        def login():
            if request.method == 'POST':
                username = request.form['username']
                password = request.form['password']
                if self.user_manager.validate_user(username, password):
                    session['user_id'] = username
                    return redirect(url_for('index'))
                else:
                    return "Credenciales incorrectas", 400
            else:
                return render_template('login.html')

        @self.app.route('/logout')
        def logout():
            session.pop('user_id', None)
            return redirect(url_for('login'))

        @self.app.route('/upload', methods=['POST'])
        def upload_file():
            if 'user_id' not in session:
                return redirect(url_for('login'))

            file = request.files.get('file')
            if not file or file.filename == '':
                return "No se envió ningún archivo", 400

            if allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(join(self.app.config['UPLOAD_FOLDER'], filename))

                self.music_player.load_songs()
                return redirect(url_for('index'))
            else:
                return "Formato no permitido", 400

        @self.app.route('/play')
        def play():
            if not self.music_player.songs or self.music_player.current_index >= len(self.music_player.songs):
                return "No hay canciones disponibles", 404

            song_path = join(self.music_player.music_folder, self.music_player.songs[self.music_player.current_index])
            return send_file(song_path, mimetype='audio/mpeg')

        @self.app.route('/next')
        def next_song():
            current_song = self.music_player.next_song()
            return jsonify({'current_song': current_song})

        @self.app.route('/select/<int:song_number>')
        def select_song(song_number):
            try:
                current_song = self.music_player.select_song(song_number)
                return jsonify({'current_song': current_song})
            except ValueError:
                return jsonify({"error": "Número de canción no válido."}), 400

        @self.app.route('/shuffle', methods=['POST'])
        def shuffle():
            self.music_player.toggle_shuffle()
            return jsonify({"status": "OK"})

    def run(self):
        self.user_manager.create_user_db()
        self.app.run(host='0.0.0.0', port=self.port, debug=True, use_reloader=False)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'mp3', 'm4a', 'wav'}

def main(music_folder, port=80):
    app = StreamingApp(music_folder, port)
    app.run()

if __name__ == '__main__':
    music_folder = "path_to_music_folder"
    port = 80 if len(argv) == 1 else int(argv[1])
    main(music_folder, port)
