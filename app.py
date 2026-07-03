import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# 1. Creamos la App
app = Flask(__name__)

# 2. Configuramos la Base de Datos
db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "connect_args": {"sslmode": "require"}
}

# 3. CREAMOS LA VARIABLE db (DESPUÉS DE LA CONFIGURACIÓN)
db = SQLAlchemy(app)

# 4. AHORA definimos las clases, YA QUE 'db' YA EXISTE
class AnuncioBusqueda(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comprador = db.Column(db.String(50), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    categoria = db.Column(db.String(30), nullable=False, default="Otros")
    producto = db.Column(db.String(100), nullable=False) 
    presupuesto_max = db.Column(db.Float, nullable=False) 
    descripcion = db.Column(db.Text, nullable=True) 
    fecha_publicacion = db.Column(db.DateTime, default=datetime.utcnow)

class Visita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)

# 5. Creamos las tablas
with app.app_context():
    db.create_all()

# 6. Resto del código (HTML y Rutas)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuscoGangas.shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 p-8 text-center">
    <h1 class="text-4xl font-bold">BuscoGangas.shop</h1>
    <p>La base de datos está conectada correctamente.</p>
</body>
</html>
"""

@app.route('/')
def inicio():
    db.session.add(Visita())
    db.session.commit()
    return render_template_string(HTML_TEMPLATE)

@app.route('/ver_busquedas')
def ver_busquedas():
    anuncios = AnuncioBusqueda.query.all()
    return jsonify([{k: v for k, v in a.__dict__.items() if k != '_sa_instance_state'} for a in anuncios])

if __name__ == '__main__':
    app.run()
