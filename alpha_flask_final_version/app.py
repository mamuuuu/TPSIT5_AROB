#Authors: Meinero Samuele, Menardi Samuele

#Importazione delle librerie necessarie al funzionamento del codice
from flask import Flask, render_template, redirect, url_for, request
import AlphaBot
import sqlite3 as sql
import time
import random
import string
import hashlib

#Oggetto della classe Flask
app = Flask(__name__)

#Istanza della classe alphabot
alpha = AlphaBot.AlphaBot()

def generatore_token():
    """
    Funzione per generare un token casuale per l'autenticazione
    """
    #Caratteri utilizzabili nella generazione
    characters = string.ascii_letters + string.digits

    # Genera una stringa alfanumerica casuale di 40 caratteri
    alphaNumeric_string = ''.join(random.choice(characters) for _ in range(40))

    return alphaNumeric_string

token = generatore_token()  # Genera un token casuale per l'autenticazione

# Funzione per validare le credenziali di accesso
def validate(username, password):
    completion = False
    con = sql.connect('./db.db')  # Connessione al database
    cur = con.cursor()
    cur.execute("SELECT * FROM USERS")  # Recupera tutti gli utenti dal database
    rows = cur.fetchall()

    #Chiusura cursore e connessione
    cur.close()
    con.close()

    for row in rows:
        dbUser = row[0]
        dbPass = row[1]
        if dbUser == username:
            completion = check_password(dbPass, password)
    return completion

def encode_hash(string):
    """
    Funzione per generare l'hash di una stringa usando l'algoritmo SHA-256
    """
    sha256 = hashlib.sha256()
    sha256.update(string.encode('utf-8'))
    hash_result = sha256.hexdigest()
    return hash_result

def check_password(hashed_password, user_password):
    """
    Funzione per verificare se una password coincide con l'hash nel database
    """
    return hashed_password == encode_hash(user_password)

# Funzione decoratore dell'app Flask
@app.route('/', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        completion = validate(username, password)
        if completion == False:
            error = 'Credenziali non valide. Riprova.'
        else:
            #Se le password sono corrette ridireziona l'utente sulla pagina principale dei comandi del robot
            return redirect(url_for('index'))
    elif request.method == 'GET':
        return render_template('login.html', error=error)

    return render_template('login.html', error=error)

# Indicizza i comandi e le relative azioni associate
COMMAND = ["RS", "SQ", "TA"]
commandDict = {"B": alpha.backward, "F": alpha.forward, "L": alpha.left, "R": alpha.right, "S": alpha.stop}

# Funzione per interrogare il database ed eseguire una sequenza di movimenti associata a una shortcut
def db_interrogation(sh):

    #print(sh)

    conn = sql.connect("./movements.db") #Connessione al db
    cursor = conn.cursor()

    cursor.execute(f"SELECT Mov_sequence FROM Movements WHERE Shortcut = '{sh}'")

    res = cursor.fetchall()

    #Chisura del cursore e della connessione
    cursor.close()
    conn.close()

    for command in res[0][0].split("-"):
        commandDict[command.split(";")[0]]()  # Esegue il comando di movimento
        time.sleep(float(command.split(";")[1]))
        alpha.stop()
        print(command)

# Funzione decoratore per gestire la pagina principale
@app.route(f"/{token}", methods=['GET', 'POST'])
def index():

    if request.method == 'POST':
        #A seconda del comando inserito -> esegue un movimento
        if request.form.get('F') == 'Forward':
            #print(">>Forward")
            alpha.forward()

        elif request.form.get('B') == 'Backward':
            #print(">>Backward")
            alpha.backward()

        elif request.form.get('S') == 'Stop':
            #print(">>Stop")
            alpha.stop()

        elif request.form.get('R') == 'Right':
            #print(">>Right")
            alpha.right()

        elif request.form.get('L') == 'Left':
            #print(">>Left")
            alpha.left()

        #Per i comandi "speciali" interroga il db
        elif request.form.get("rs") == "RS":
            db_interrogation("RS")

        elif request.form.get("ta") == "TA":
            db_interrogation("TA")

        elif request.form.get("sq") == "SQ":
            db_interrogation("SQ")

        else:
            print("Unknown")

    elif request.method == 'GET':
        return render_template('index.html')

    return render_template("index.html")

# Esegue l'app Flask
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
