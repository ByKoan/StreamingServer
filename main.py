import sqlite3
from flask import Flask, jsonify, render_template_string, request, send_file, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import threading
import os
import time
import random

app = Flask(__name__)
app.secret_key = os.urandom(512)  # Clave secreta para manejar sesiones

# Ruta de la carpeta de música
# MUSIC_FOLDER = r"Put here your root" # - Windows
# MUSIC_FOLDER = "Put here your root" # - Linux

songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.m4a', '.wav'))]
current_index = 0
shuffle_mode = False
UPLOAD_FOLDER = MUSIC_FOLDER  # Carpeta donde se almacenan las canciones subidas
ALLOWED_EXTENSIONS = {'mp3', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Crear base de datos y tabla de usuarios si no existen
def create_user_db():
    conn = get_db_connection()
    conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    conn.commit()
    conn.close()

# Añadir un usuario de ejemplo (se puede usar solo una vez para la creación del usuario)
def add_user(username, password):
    conn = get_db_connection()
    hashed_password = generate_password_hash(password)
    conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    conn.commit()
    conn.close()

# Validar usuario
def validate_user(username, password):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()
    if user and check_password_hash(user['password'], password):
        return True
    return False

# Función para verificar extensiones permitidas
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'file' not in request.files:
            return "No se envió ningún archivo", 400
        file = request.files['file']
        if file.filename == '':
            return "El archivo no tiene nombre", 400
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # Actualizar la lista de canciones
            global songs
            songs = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.m4a'))]
            return redirect(url_for('index'))

def play_music_in_background():
    global current_index
    while True:
        if not songs:
            print("No hay canciones en la carpeta.")
            time.sleep(1)
            continue
        print(f"Reproduciendo en segundo plano: {songs[current_index]}")
        with app.app_context():
            next_song()
        time.sleep(180)

def start_background_thread():
    thread = threading.Thread(target=play_music_in_background)
    thread.daemon = True
    thread.start()

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir a la página de login si no está logueado

    global current_index
    if not songs:
        return """
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>No hay canciones disponibles</title>
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        background: linear-gradient(to right, #1d2671, #c33764);
                        color: #fff;
                        text-align: center;
                        padding: 20px;
                        margin: 0;
                    }
                    h1 {
                        font-size: 40px;
                        margin-bottom: 20px;
                    }
                    p {
                        font-size: 20px;
                        color: #ff4c4c;
                    }
                    .info-box {
                        background-color: rgba(0, 0, 0, 0.6);
                        padding: 20px;
                        border-radius: 8px;
                        display: inline-block;
                        margin-top: 30px;
                    }
                    .info-box h2 {
                        font-size: 24px;
                        color: #4caf50;
                    }
                    .info-box p {
                        font-size: 18px;
                        color: #fff;
                    }
                    .logout {
                        position: absolute;
                        top: 20px;
                        right: 20px;
                        background-color: #ff4c4c;
                        color: white;
                        font-size: 14px;
                        padding: 10px 15px;
                        border: none;
                        border-radius: 5px;
                        cursor: pointer;
                    }
                    .logout:hover {
                        background-color: #e43f3f;
                    }
                </style>
            </head>
            <body>
                <button class="logout" onclick="window.location.href='/logout'">Cerrar sesión</button>
                <h1>No hay canciones disponibles</h1>
                <div class="info-box">
                    <h2>Selecciona la carpeta desde el programa</h2>
                    <p>Por favor selecciona la carpeta donde están ubicados tus archivos de música desde el programa y vuelve a cargar la página para comenzar a reproducir canciones.</p>
                </div>
            </body>
            </html>
        """

    song_table = "<ul style='list-style: none; padding: 0;'>"
    for i, song in enumerate(songs):
        style = f"padding: 10px; margin: 5px; background-color: {'#4caf50' if i == current_index else '#f9f9f9'}; color: {'#fff' if i == current_index else '#333'}; border-radius: 8px; text-align: left; cursor: pointer;"
        song_table += f"<li style='{style}' onclick='selectSong({i + 1})'>{i + 1}. {song}</li>"
    song_table += "</ul>"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Streaming Server</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(to right, #1d2671, #c33764);
                color: #fff;
                text-align: center;
                padding: 20px;
                margin: 0;
            }}
            h1 {{
                margin-bottom: 10px;
            }}
            audio {{
                margin: 20px auto;
                display: block;
                width: 80%;
                max-width: 600px;
            }}
            button {{
                background-color: #4caf50;
                border: none;
                color: white;
                padding: 10px 20px;
                text-align: center;
                text-decoration: none;
                display: inline-block;
                font-size: 16px;
                margin: 10px;
                cursor: pointer;
                border-radius: 5px;
            }}
            button:hover {{
                background-color: #45a049;
            }}
            .logout {{
                position: absolute;
                top: 20px;
                right: 20px;
                background-color: #ff4c4c;
                color: white;
                font-size: 14px;
                padding: 10px 15px;
                border: none;
                border-radius: 5px;
                cursor: pointer;
            }}
            .logout:hover {{
                background-color: #e43f3f;
            }}
            ul {{
                max-width: 600px;
                margin: 20px auto;
                padding: 0;
            }}
            ul li:hover {{
                background-color: #ddd;
                color: #000;
            }}
            .toggle {{
                display: flex;
                align-items: center;
                justify-content: center;
                margin: 20px 0;
            }}
            .toggle label {{
                margin-left: 10px;
                font-size: 18px;
                cursor: pointer;
            }}
            .switch {{
                position: relative;
                display: inline-block;
                width: 40px;
                height: 20px;
            }}
            .switch input {{
                display: none;
            }}
            .slider {{
                position: absolute;
                cursor: pointer;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                background-color: #ccc;
                transition: .4s;
                border-radius: 20px;
            }}
            .slider:before {{
                position: absolute;
                content: "";
                height: 14px;
                width: 14px;
                left: 3px;
                bottom: 3px;
                background-color: white;
                transition: .4s;
                border-radius: 50%;
            }}
            input:checked + .slider {{
                background-color: #4caf50;
            }}
            input:checked + .slider:before {{
                transform: translateX(20px);
            }}
        </style>
    </head>
    <body>
        <button class="logout" onclick="window.location.href='/logout'">Cerrar sesión</button>
        <h1>Servidor Streaming</h1>
        <audio id="audio-player" controls onended="nextSong()">
            <source id="audio-source" src="/play?{int(time.time())}" type="audio/mpeg">
            Tu navegador no soporta el elemento de audio.
        </audio>
        <p>Canción actual: <strong id="current-song">{songs[current_index]}</strong></p>
        <button onclick="nextSong()">Siguiente Canción</button>
        <div class="toggle">
            <label class="switch">
                <input type="checkbox" id="shuffle-toggle" onchange="toggleShuffle()">
                <span class="slider"></span>
            </label>
            <label for="shuffle-toggle">Modo Aleatorio</label>
        </div>
        <form action="/upload" method="post" enctype="multipart/form-data" style="margin-top: 20px; text-align: center;">
            <label for="file-upload" style="display: inline-block; background-color: #4caf50; color: white; padding: 10px 20px; font-size: 16px; border-radius: 5px; cursor: pointer; margin-right: 10px;">
                Seleccionar archivo
                <input type="file" id="file-upload" name="file" accept=".mp3,.m4a" style="display: none;" required>
            </label>
            <button type="submit" style="background-color: #4caf50; color: white; padding: 10px 20px; font-size: 16px; border: none; border-radius: 5px; cursor: pointer;">
                Subir Canción
            </button>
        </form>

        <h2>Lista de Canciones</h2>
        {song_table}
<script>
    function toggleShuffle() {{
        fetch('/shuffle', {{ method: 'POST' }}).then(response => response.json())
            .then(data => console.log("Modo aleatorio actualizado."));
    }}
    
    function nextSong() {{
        fetch('/next')
            .then(response => response.json())
            .then(data => {{
                // Actualiza el nombre de la canción actual
                document.getElementById('current-song').textContent = data.current_song;
                
                // Actualiza la lista de canciones
                const audioPlayer = document.getElementById('audio-player');
                document.getElementById('audio-source').src = "/play?" + Date.now();
                audioPlayer.load();
                audioPlayer.play(); // Forzar la reproducción

                // Actualizamos la visualización de la lista de canciones (resaltar la actual)
                const songs = document.querySelectorAll('ul li');
                songs.forEach(function(song) {{
                    const songText = song.textContent.trim();
                    if (songText === data.current_song) {{
                        song.style.backgroundColor = '#4caf50';  // Resaltamos la canción actual
                        song.style.color = '#fff';  // Aseguramos que el texto sea blanco
                    }} else {{
                        song.style.backgroundColor = '#f9f9f9';  // Vuelve al color normal para las demás
                        song.style.color = '#333';  // Aseguramos el color para las canciones no actuales
                    }}
                }});
            }});
    }}

    function selectSong(songNumber) {{
        fetch(`/select/${{songNumber}}`)
            .then(response => response.json())
            .then(data => {{
                // Actualiza el nombre de la canción actual
                document.getElementById('current-song').textContent = data.current_song;

                // Actualiza la lista de canciones
                const audioPlayer = document.getElementById('audio-player');
                document.getElementById('audio-source').src = "/play?" + Date.now();
                audioPlayer.load();
                audioPlayer.play(); // Forzar la reproducción

                // Actualizamos la visualización de la lista de canciones (resaltar la actual)
                const songs = document.querySelectorAll('ul li');
                songs.forEach(function(song) {{
                    const songText = song.textContent.trim();
                    if (songText === data.current_song) {{
                        song.style.backgroundColor = '#4caf50';  // Resaltamos la canción actual
                        song.style.color = '#fff';  // Aseguramos que el texto sea blanco
                    }} else {{
                        song.style.backgroundColor = '#f9f9f9';  // Vuelve al color normal para las demás
                        song.style.color = '#333';  // Aseguramos el color para las canciones no actuales
                    }}
                }});
            }});
    }}
</script>

    </body>
    </html>
    """
    return render_template_string(html)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if validate_user(username, password):
            session['user_id'] = username  # Guarda el nombre de usuario en la sesión
            return redirect(url_for('index'))
        else:
            # Si las credenciales son incorrectas, mostramos el formulario con un mensaje de error
            return '''
                <!DOCTYPE html>
                <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Iniciar Sesión</title>
                    <style>
                        body {
                            font-family: Arial, sans-serif;
                            background: linear-gradient(to right, #1d2671, #c33764);
                            color: #fff;
                            text-align: center;
                            padding: 50px;
                        }
                        h1 {
                            font-size: 40px;
                            margin-bottom: 20px;
                        }
                        form {
                            background-color: rgba(0, 0, 0, 0.6);
                            padding: 30px;
                            border-radius: 8px;
                            display: inline-block;
                        }
                        input[type="text"], input[type="password"] {
                            width: 300px;
                            padding: 10px;
                            margin: 10px 0;
                            border: 1px solid #ccc;
                            border-radius: 5px;
                            background-color: #f1f1f1;
                        }
                        input[type="submit"] {
                            width: 320px;
                            padding: 10px;
                            background-color: #4caf50;
                            color: white;
                            font-size: 16px;
                            border: none;
                            border-radius: 5px;
                            cursor: pointer;
                            margin-top: 10px;
                        }
                        input[type="submit"]:hover {
                            background-color: #45a049;
                        }
                        label {
                            font-size: 18px;
                            color: #fff;
                        }
                        .error-message {
                            color: #ff4c4c;
                            margin-bottom: 20px;
                        }
                    </style>
                </head>
                <body>
                    <h1>Iniciar Sesión</h1>
                    <p class="error-message">Credenciales incorrectas. Por favor intente nuevamente.</p>
                    <form method="post">
                        <label for="username">Usuario:</label><br>
                        <input type="text" id="username" name="username" required><br><br>
                        <label for="password">Contraseña:</label><br>
                        <input type="password" id="password" name="password" required><br><br>
                        <input type="submit" value="Iniciar sesión">
                    </form>
                </body>
                </html>
            '''
    
    # Si no se ha enviado el formulario, mostramos el formulario vacío
    return '''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Iniciar Sesión</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    background: linear-gradient(to right, #1d2671, #c33764);
                    color: #fff;
                    text-align: center;
                    padding: 50px;
                }
                h1 {
                    font-size: 40px;
                    margin-bottom: 20px;
                }
                form {
                    background-color: rgba(0, 0, 0, 0.6);
                    padding: 30px;
                    border-radius: 8px;
                    display: inline-block;
                }
                input[type="text"], input[type="password"] {
                    width: 300px;
                    padding: 10px;
                    margin: 10px 0;
                    border: 1px solid #ccc;
                    border-radius: 5px;
                    background-color: #f1f1f1;
                }
                input[type="submit"] {
                    width: 320px;
                    padding: 10px;
                    background-color: #4caf50;
                    color: white;
                    font-size: 16px;
                    border: none;
                    border-radius: 5px;
                    cursor: pointer;
                    margin-top: 10px;
                }
                input[type="submit"]:hover {
                    background-color: #45a049;
                }
                label {
                    font-size: 18px;
                    color: #fff;
                }
            </style>
        </head>
        <body>
            <h1>Iniciar Sesión</h1>
            <form method="post">
                <label for="username">Usuario:</label><br>
                <input type="text" id="username" name="username" required><br><br>
                <label for="password">Contraseña:</label><br>
                <input type="password" id="password" name="password" required><br><br>
                <input type="submit" value="Iniciar sesión">
            </form>
        </body>
        </html>
    '''
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina el usuario de la sesión
    return redirect(url_for('login'))

@app.route('/play')
def play():
    song_path = os.path.join(MUSIC_FOLDER, songs[current_index])
    return send_file(song_path)

@app.route('/next')
def next_song():
    global current_index

    if shuffle_mode:
        # Elegir un índice aleatorio diferente al actual
        current_index = random.choice([i for i in range(len(songs)) if i != current_index])
    else:
        # Avanzar al siguiente índice de forma secuencial
        current_index = (current_index + 1) % len(songs)
    
    return jsonify({'current_song': songs[current_index]})

@app.route('/select/<int:song_number>')
def select_song(song_number):
    global current_index
    if song_number < 1 or song_number > len(songs):
        return jsonify({"error": "Número de canción no válido."}), 400
    current_index = song_number - 1
    return jsonify({"current_song": songs[current_index]})

@app.route('/shuffle', methods=['POST'])
def shuffle():
    global shuffle_mode
    shuffle_mode = not shuffle_mode
    return jsonify({"status": "OK"})

if __name__ == '__main__':
    create_user_db()  # Crear base de datos si no existe
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)
