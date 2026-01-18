from flask import Flask, request, jsonify, render_template
import sqlite3, hashlib

app = Flask(__name__)

# ======= DATABASE =======
def db():
    return sqlite3.connect("database.db")

def hash_pw(p):
    return hashlib.sha256(p.encode()).hexdigest()

# ======= FRONT =======
@app.route("/")
def index():
    return render_template("index.html")

# ======= USERS =======
@app.route("/register", methods=["POST"])
def register():
    d = request.json
    try:
        cur = db()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (d["username"], hash_pw(d["password"]))
        )
        cur.commit()
        return {"ok": True}
    except:
        return {"error": "username exists"}, 400

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    cur = db()
    row = cur.execute(
        "SELECT id FROM users WHERE username=? AND password_hash=?",
        (d["username"], hash_pw(d["password"]))
    ).fetchone()
    return {"user_id": row[0]} if row else ({"error": "invalid"}, 401)

@app.route("/search")
def search():
    q = request.args.get("q", "")
    cur = db()
    rows = cur.execute(
        "SELECT id, username FROM users WHERE username LIKE ? LIMIT 20",
        (f"%{q}%",)
    ).fetchall()
    return jsonify([{"id": r[0], "username": r[1]} for r in rows])

# ======= DM =======
@app.route("/dm/send", methods=["POST"])
def send_dm():
    d = request.json
    cur = db()
    cur.execute(
        "INSERT INTO private_messages (sender_id, receiver_id, message) VALUES (?,?,?)",
        (d["from"], d["to"], d["msg"])
    )
    cur.commit()
    return {"sent": True}

@app.route("/dm/history")
def dm_history():
    a = request.args["a"]
    b = request.args["b"]
    cur = db()
    rows = cur.execute("""
        SELECT sender_id, message, created_at FROM private_messages
        WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
        ORDER BY id
    """, (a,b,b,a)).fetchall()
    return jsonify(rows)

# ======= GROUPS =======
@app.route("/group/create", methods=["POST"])
def create_group():
    d = request.json
    cur = db()
    cur.execute("INSERT INTO groups (name, owner_id) VALUES (?,?)", (d["name"], d["owner"]))
    gid = cur.execute("SELECT last_insert_rowid()").fetchone()[0]
    cur.execute("INSERT INTO group_members VALUES (?,?)", (gid, d["owner"]))
    cur.commit()
    return {"group_id": gid}

@app.route("/group/send", methods=["POST"])
def group_send():
    d = request.json
    cur = db()
    cur.execute(
        "INSERT INTO group_messages (group_id, sender_id, message) VALUES (?,?,?)",
        (d["group"], d["from"], d["msg"])
    )
    cur.commit()
    return {"sent": True}

if name == "__main__":
    app.run(debug=True)