from werkzeug.security  import generate_password_hash, check_password_hash
from sqlite3            import Row, connect

class UserManager:
    def __init__(self, db_name='users.db'):
        self.db_name = db_name

    def get_db_connection(self):
        conn = connect(self.db_name)
        conn.row_factory = Row
        return conn

    def create_user_db(self):
        conn = self.get_db_connection()
        conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def add_user(self, username, password):
        conn = self.get_db_connection()
        hashed_password = generate_password_hash(password)
        conn.execute('INSERT INTO users (username, password) VALUES (?, ?)', (username, hashed_password))
        conn.commit()
        conn.close()

    def validate_user(self, username, password):
        conn = self.get_db_connection()
        user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user['password'], password):
            return True
        return False