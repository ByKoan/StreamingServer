import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from colorama import Fore, Back, Style, init

# Inicializar colorama
init(autoreset=True)

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

# Mostrar todos los usuarios y contraseñas encriptadas
def show_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM users').fetchall()
    conn.close()

    if users:
        print("\n" + Fore.GREEN + f"{'ID':<5}{'Username':<20}{'Password (Hash)'}")
        for user in users:
            print(Fore.CYAN + f"{user['id']:<5}{user['username']:<20}{user['password']}")
    else:
        print(Fore.RED + "No hay usuarios en la base de datos.")
    print("\n")

# Función para crear un nuevo usuario
def create_user():
    username = input(Fore.YELLOW + "Ingresa el nombre de usuario: ")
    password = input(Fore.YELLOW + "Ingresa la contraseña: ")
    add_user(username, password)
    print(Fore.GREEN + "\nUsuario creado exitosamente.\n")

# Función para eliminar un usuario
def delete_user():
    username = input(Fore.YELLOW + "Ingresa el nombre del usuario a eliminar: ")
    conn = get_db_connection()
    conn.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()
    print(Fore.GREEN + f"\nUsuario {username} eliminado exitosamente.\n")

# Función para cambiar la contraseña de un usuario
def change_password():
    username = input(Fore.YELLOW + "Ingresa el nombre del usuario: ")
    new_password = input(Fore.YELLOW + "Ingresa la nueva contraseña: ")
    conn = get_db_connection()
    hashed_password = generate_password_hash(new_password)
    conn.execute('UPDATE users SET password = ? WHERE username = ?', (hashed_password, username))
    conn.commit()
    conn.close()
    print(Fore.GREEN + f"\nContraseña del usuario {username} cambiada exitosamente.\n")

# Función para cambiar el nombre de un usuario
def change_username():
    old_username = input(Fore.YELLOW + "Ingresa el nombre del usuario actual: ")
    new_username = input(Fore.YELLOW + "Ingresa el nuevo nombre de usuario: ")
    
    conn = get_db_connection()
    conn.execute('UPDATE users SET username = ? WHERE username = ?', (new_username, old_username))
    conn.commit()
    conn.close()
    print(Fore.GREEN + f"\nNombre de usuario de {old_username} cambiado a {new_username} exitosamente.\n")

# Función para mostrar el menú con colores y opciones
def show_menu():
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

    while True:
        show_menu()
        choice = input(Fore.YELLOW + "Selecciona una opción: ")

        if choice == '1':
            create_user()
        elif choice == '2':
            delete_user()
        elif choice == '3':
            change_password()
        elif choice == '4':
            change_username()
        elif choice == '5':
            show_users()
        elif choice == '6':
            print(Fore.RED + "\nSaliendo...\n")
            break
        else:
            print(Fore.RED + "\nOpción no válida. Por favor, selecciona de nuevo.\n")

if __name__ == "__main__":
    main()
