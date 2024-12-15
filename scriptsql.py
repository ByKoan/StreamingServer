from werkzeug.security import generate_password_hash, check_password_hash
from colorama          import Fore, Style, init
from colorama.ansi     import clear_screen
from sqlite3           import connect, Row, IntegrityError
from getpass           import getpass, _raw_input
from sys               import exit

def raw_input_(prompt):
    while True:
        try:
            return _raw_input(prompt)
        except KeyboardInterrupt:
            print("\r")

# Conexión a la base de datos SQLite
def get_db_connection():
    conn = connect('users.db')
    conn.row_factory = Row
    return conn

# Crear base de datos y tabla de usuarios si no existen
def create_user_db():
    conn = get_db_connection()
    try:
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
    finally:
        conn.commit()
        conn.close()

# Añadir un usuario de ejemplo (se puede usar solo una vez para la creación del usuario)
def add_user(username, password):
    conn = get_db_connection()
    try:
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
    finally:
        conn.commit()
        conn.close()

# Validar usuario
def validate_user(username, password):
    conn = get_db_connection()
    try: user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    finally: conn.close()
    return user and check_password_hash(user['password'], password)

# Mostrar todos los usuarios y contraseñas encriptadas
def show_users(print=print):
    conn = get_db_connection()
    try: users = conn.execute('SELECT * FROM users').fetchall()
    finally: conn.close()

    if users:
        print("\n" + Fore.GREEN + f"{'ID':<5}{'Username':<20}{'Password (Hash)'}")
        for user in users:
            print(Fore.CYAN + f"{user['id']:<5}{user['username']:<20}{user['password']}")
    else:
        print(Fore.RED + "No hay usuarios en la base de datos.")
    print("\n")
    return users

# Función para crear un nuevo usuario
def create_user():
    while True:
        username = raw_input_(Fore.YELLOW + "Ingresa el nombre de usuario: ")
        password = getpass(Fore.YELLOW + "Ingresa la contraseña: ")
        try:
            add_user(username, password)
            print(Fore.GREEN + "\nUsuario creado exitosamente.\n")
            break
        except IntegrityError:
            print(Fore.RED + "\nUsuario ya existente.\n")

# Función para eliminar un usuario
def delete_user():
    def print_nothing(*args, **kwargs): pass
    users = show_users(print=print_nothing)
    username = raw_input_(Fore.YELLOW + "Ingresa el nombre del usuario a eliminar: ")
    """list_users
    for user in users:
        print(user['username'])"""
    conn = get_db_connection()
    try: 
        user = conn.execute('SELECT username FROM users WHERE username = ?', (username,)).fetchall()
        try: 
            conn.execute('DELETE FROM users WHERE username = ?', (list(user[0])[0],))
            print(Fore.GREEN + f"\nUsuario {username} eliminado exitosamente.\n")
        except IndexError: print(Fore.RED + f"\nEl usuario {username} no existe.\n")
    finally:
        conn.commit()
        conn.close()

# Función para cambiar la contraseña de un usuario
def change_password():
    username = raw_input_(Fore.YELLOW + "Ingresa el nombre del usuario: ")
    new_password = getpass(Fore.YELLOW + "Ingresa la nueva contraseña: ")
    conn = get_db_connection()
    hashed_password = generate_password_hash(new_password)
    try: conn.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))
    finally:
        conn.commit()
        conn.close()
    print(Fore.GREEN + f"\nContraseña del usuario {username} cambiada exitosamente.\n")

# Función para cambiar el nombre de un usuario
def change_username():
    old_username = raw_input_(Fore.YELLOW + "Ingresa el nombre del usuario actual: ")
    new_username = raw_input_(Fore.YELLOW + "Ingresa el nuevo nombre de usuario: ")
    
    conn = get_db_connection()
    try:
        conn.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, old_username))
    finally:
        conn.commit()
        conn.close()
    print(Fore.GREEN + f"\nNombre de usuario de {old_username} cambiado a {new_username} exitosamente.\n")

# Función para mostrar el menú con colores y opciones
def show_menu():
    print(Fore.MAGENTA + Style.BRIGHT + "\nMade By Koan")
    print(Fore.MAGENTA + Style.BRIGHT + "\nMenú de Opciones:")
    print(Fore.CYAN + "1. Crear usuario")
    print(Fore.CYAN + "2. Eliminar usuario")
    print(Fore.CYAN + "3. Cambiar contraseña de usuario")
    print(Fore.CYAN + "4. Cambiar nombre de usuario")
    print(Fore.CYAN + "5. Ver usuarios")
    print(Fore.RED + "6. Salir")

# Función principal para manejar la lógica del menú
def main():
    create_user_db()  # Crear base de datos si no existe
    options = [
        create_user,
        delete_user,
        change_password,
        change_username,
        show_users
    ]
    print(clear_screen())
    while True:
        show_menu()
        try:
            choice = int(raw_input_(Fore.YELLOW + "Selecciona una opción: "))
            if choice >= 1 and len(options)+1 > choice:
                options[choice-1]()
            elif choice == 6:
                print(Fore.RED + "\nSaliendo...\n")
                exit(0)
            else:
                raise ValueError("Esta opcion no está disponible.")
        except ValueError:
            print(Fore.RED + "\nOpción no válida. Por favor, selecciona de nuevo.\n")
        raw_input_("presione una tecla para continuar...")
        print(clear_screen())

if __name__ == "__main__":
    # Inicializar colorama
    init(autoreset=True)
    main()
