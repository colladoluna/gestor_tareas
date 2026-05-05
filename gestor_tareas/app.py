from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
DB_PATH = "tareas.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tareas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            descripcion TEXT,
            prioridad TEXT DEFAULT 'media',
            completada INTEGER DEFAULT 0,
            fecha_creacion TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    filtro = request.args.get("filtro", "todas")
    conn = get_db()
    if filtro == "pendientes":
        tareas = conn.execute("SELECT * FROM tareas WHERE completada = 0 ORDER BY fecha_creacion DESC").fetchall()
    elif filtro == "completadas":
        tareas = conn.execute("SELECT * FROM tareas WHERE completada = 1 ORDER BY fecha_creacion DESC").fetchall()
    else:
        tareas = conn.execute("SELECT * FROM tareas ORDER BY fecha_creacion DESC").fetchall()

    total = conn.execute("SELECT COUNT(*) FROM tareas").fetchone()[0]
    completadas = conn.execute("SELECT COUNT(*) FROM tareas WHERE completada = 1").fetchone()[0]
    conn.close()
    return render_template("index.html", tareas=tareas, filtro=filtro, total=total, completadas=completadas)

@app.route("/nueva", methods=["POST"])
def nueva_tarea():
    titulo = request.form.get("titulo", "").strip()
    descripcion = request.form.get("descripcion", "").strip()
    prioridad = request.form.get("prioridad", "media")
    if titulo:
        conn = get_db()
        conn.execute(
            "INSERT INTO tareas (titulo, descripcion, prioridad, fecha_creacion) VALUES (?, ?, ?, ?)",
            (titulo, descripcion, prioridad, datetime.now().strftime("%d/%m/%Y %H:%M"))
        )
        conn.commit()
        conn.close()
    return redirect(url_for("index"))

@app.route("/completar/<int:id>")
def completar(id):
    conn = get_db()
    conn.execute("UPDATE tareas SET completada = NOT completada WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/eliminar/<int:id>")
def eliminar(id):
    conn = get_db()
    conn.execute("DELETE FROM tareas WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

@app.route("/editar/<int:id>", methods=["GET", "POST"])
def editar(id):
    conn = get_db()
    if request.method == "POST":
        titulo = request.form.get("titulo", "").strip()
        descripcion = request.form.get("descripcion", "").strip()
        prioridad = request.form.get("prioridad", "media")
        if titulo:
            conn.execute(
                "UPDATE tareas SET titulo = ?, descripcion = ?, prioridad = ? WHERE id = ?",
                (titulo, descripcion, prioridad, id)
            )
            conn.commit()
        conn.close()
        return redirect(url_for("index"))
    tarea = conn.execute("SELECT * FROM tareas WHERE id = ?", (id,)).fetchone()
    conn.close()
    return render_template("editar.html", tarea=tarea)

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
