# Python Streaming Server
***Python music streaming server***
- **Libs used: flask (html server) sqlite3 (database) and werkzeug.security for password of database

***Functions of the server:***
- Bassically it is a server that stream music of download files on the root you selected (You need to do it before run it)
- It has function like upload songs, listen random songs in your list and listen songs with a click in the list

***If you wanna compile it run this commands***
```bash
pip install pyinstaller 
pyinstaller --name StreamingServer --onefile --hidden-import flask --noconsole main.py
```
