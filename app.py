from flask import Flask, request, jsonify, render_template
import sqlite3, hashlib, os

app = Flask(__name__)

# ======= DATABASE =======
def db():
    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row
    return conn

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
        conn = db()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (?,?)",
            (d["username"], hash_pw(d["password"]))
        )
        conn.commit()
        conn.close()
        return {"ok": True}
    except sqlite3.IntegrityError:
        return {"error": "username exists"}, 400

@app.route("/login", methods=["POST"])
def login():
    d = request.json
    conn = db()
    cur = conn.cursor()
    row = cur.execute(
        "SELECT id FROM users WHERE username=? AND password_hash=?",
        (d["username"], hash_pw(d["password"]))
    ).fetchone()
    conn.close()
    return {"user_id": row["id"]} if row else ({"error": "invalid"}, 401)

@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = db()
    cur = conn.cursor()
    rows = cur.execute(
        "SELECT id, username FROM users WHERE username LIKE ? LIMIT 20",
        (f"%{q}%",)
    ).fetchall()
    conn.close()
    return jsonify([{"id": r["id"], "username": r["username"]} for r in rows])

# ======= DM =======
@app.route("/dm/send", methods=["POST"])
def send_dm():
    d = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO private_messages (sender_id, receiver_id, message) VALUES (?,?,?)",
        (d["from"], d["to"], d["msg"])
    )
    conn.commit()
    conn.close()
    return {"sent": True}

@app.route("/dm/history")
def dm_history():
    a = request.args["a"]
    b = request.args["b"]
    conn = db()
    cur = conn.cursor()
    rows = cur.execute("""
        SELECT sender_id, message, created_at FROM private_messages
        WHERE (sender_id=? AND receiver_id=?) OR (sender_id=? AND receiver_id=?)
        ORDER BY id
    """, (a,b,b,a)).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])

# ======= GROUPS =======
@app.route("/group/create", methods=["POST"])
def create_group():
    d = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute("INSERT INTO groups (name, owner_id) VALUES (?,?)", (d["name"], d["owner"]))
    gid = cur.execute("SELECT last_insert_rowid()").fetchone()[0]
    cur.execute("INSERT INTO group_members VALUES (?,?)", (gid, d["owner"]))
    conn.commit()
    conn.close()
    return {"group_id": gid}

@app.route("/group/send", methods=["POST"])
def group_send():
    d = request.json
    conn = db()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO group_messages (group_id, sender_id, message) VALUES (?,?,?)",
        (d["group"], d["from"], d["msg"])
    )
    conn.commit()
    conn.close()
    return {"sent": True}

# ======= RUN SERVER =======
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
