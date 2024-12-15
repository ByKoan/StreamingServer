from flask              import Flask, jsonify, render_template, request, send_file, redirect, url_for, session
from werkzeug.security  import generate_password_hash, check_password_hash
from werkzeug.utils     import secure_filename
from sqlite3            import Row, connect
from os                 import listdir, urandom
from os.path            import join
from threading          import Thread
from time               import sleep, time
from random             import choice
from sys                import argv, exit


app = Flask(
    __name__,
    template_folder=join("..", "templates"),
    static_folder=join("..", "static")
)

app.secret_key = urandom(512)  # Clave secreta para manejar sesiones
dir_templates = join("..", "templates")


# Ruta de la carpeta de música
# MUSIC_FOLDER = r"Put here your root" # - Windows
# MUSIC_FOLDER = "Put here your root" # - Linux
MUSIC_FOLDER = r"D:\downloader\music\Music.anon"
songs = [f for f in listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.m4a', '.wav'))]
current_index = 0
shuffle_mode = False
UPLOAD_FOLDER = MUSIC_FOLDER  # Carpeta donde se almacenan las canciones subidas
ALLOWED_EXTENSIONS = {'mp3', 'm4a'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = connect('users.db')
    conn.row_factory = Row
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

@app.route('/upload', methods=['POST'])
def upload_file():
    global songs
    if 'user_id' not in session:
        return redirect(url_for('login'))

    file = request.files.get('file')
    if not file or file.filename == '':
        return "No se envió ningún archivo", 400

    if allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(join(app.config['UPLOAD_FOLDER'], filename))
        
        # Actualizar la lista de canciones
        songs = [f for f in listdir(MUSIC_FOLDER) if f.endswith(('.mp3', '.m4a', '.wav'))]
        print(f"Archivo subido: {filename}")
        return redirect(url_for('index'))
    else:
        return "Formato no permitido", 400

def play_music_in_background():
    global songs
    while True:
        if not songs:
            print("No hay canciones en la carpeta.")
            # sleep(1) # nunca hacer esto, puede dejar el servidor sin atener peticiones
            continue
        print(f"Reproduciendo en segundo plano: {songs[current_index]}")
        with app.app_context():
            next_song()
        # sleep(180) # nunca hacer esto, puede dejar el servidor sin atener peticiones

def start_background_thread():
    thread = Thread(target=play_music_in_background)
    thread.daemon = True
    thread.start()
    return thread

@app.route('/', methods=['GET', 'POST'])
def index():
    global current_index, songs
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirigir a la página de login si no está logueado

    if not songs: return render_template('/no_index.html')

    song_table = "<ul style='list-style: none; padding: 0;'>"
    for i, song in enumerate(songs):
        style = f"padding: 10px; margin: 5px; background-color: {'#4caf50' if i == current_index else '#f9f9f9'}; color: {'#fff' if i == current_index else '#333'}; border-radius: 8px; text-align: left; cursor: pointer;"
        song_table += f"<li style='{style}' onclick='selectSong({i + 1})'>{i + 1}. {song}</li>"
    song_table += "</ul>"

    return render_template('/index.html',
        song_table=song_table,
        song_now=songs[current_index],
        play_url=f"/play?{int(time())}"
    )

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
            return str()
    else: # GET
        # Si no se ha enviado el formulario, mostramos el formulario vacío
        return render_template('/login.html')
    
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Elimina el usuario de la sesión
    return redirect(url_for('login'))

@app.route('/play')
def play():
    global current_index, songs
    if not songs or current_index >= len(songs):
        return "No hay canciones disponibles", 404

    song_path = join(MUSIC_FOLDER, songs[current_index])
    return send_file(song_path, mimetype='audio/mpeg')

@app.route('/next')
def next_song():
    global current_index, shuffle_mode
    if shuffle_mode:
        # Elegir un índice aleatorio diferente al actual
        current_index = choice([i for i in range(len(songs)) if i != current_index])
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
    
    if len(argv) != 1:
        try: port = int(argv[1])
        except TypeError:
            print("El puerto debe ser un número entero.")
            exit(1)
    else: port = 80
    
    app.run(host='0.0.0.0', 
            port=port, 
            debug=False, 
            use_reloader=False)
