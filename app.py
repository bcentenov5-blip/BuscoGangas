import os
from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

db_url = os.environ.get('DATABASE_URL')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql+psycopg2://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    "pool_pre_ping": True,
    "connect_args": {"sslmode": "require"}
}

db = SQLAlchemy(app)

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

with app.app_context():
    db.create_all()

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuscoGangas.shop</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen">
    <div class="max-w-5xl mx-auto p-4 grid grid-cols-1 md:grid-cols-3 gap-8">
        <section class="md:col-span-1">
            <form id="formGanga" class="bg-slate-950 border border-slate-800 p-6 rounded-2xl space-y-4">
                <h2 class="text-xl font-bold">🚀 Publicar Búsqueda</h2>
                <input type="text" id="comprador" placeholder="Nombre" required class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm">
                <input type="tel" id="telefono" placeholder="WhatsApp" required class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm">
                <select id="categoria" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm">
                    <option value="Tecnología">Tecnología</option>
                    <option value="Videojuegos">Videojuegos</option>
                    <option value="Ropa">Ropa</option>
                    <option value="Hogar">Hogar</option>
                    <option value="Otros">Otros</option>
                </select>
                <input type="text" id="producto" placeholder="Producto" required class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm">
                <input type="number" id="presupuesto" placeholder="Presupuesto" required class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm">
                <textarea id="descripcion" placeholder="Detalles..." class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-sm"></textarea>
                <button type="submit" class="w-full bg-cyan-500 text-slate-950 font-bold py-2 rounded-xl">Publicar</button>
            </form>
        </section>
        <section class="md:col-span-2 space-y-4">
            <input type="text" id="buscador" oninput="renderizar()" placeholder="🔍 Buscar productos..." class="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2 text-sm">
            <div id="contenedorAnuncios" class="space-y-4"></div>
        </section>
    </div>
    <script>
        let anuncios = [];
        async function cargar() {
            const res = await fetch('/ver_busquedas');
            anuncios = await res.json();
            renderizar();
        }
        function renderizar() {
            const busqueda = document.getElementById('buscador').value.toLowerCase();
            const cont = document.getElementById('contenedorAnuncios');
            const filtrados = anuncios.filter(a => a.producto.toLowerCase().includes(busqueda));
            cont.innerHTML = filtrados.map(a => `
                <div class="bg-slate-950 border border-slate-800 p-4 rounded-xl">
                    <h3 class="font-bold">${a.producto}</h3>
                    <p class="text-emerald-400">₡${a.presupuesto_max.toLocaleString('es-CR')}</p>
                    <a href="https://wa.me/${a.telefono}" target="_blank" class="text-cyan-400 text-xs">Contactar por WhatsApp</a>
                </div>
            `).join('');
        }
        document.getElementById('formGanga').addEventListener('submit', async (e) => {
            e.preventDefault();
            const datos = {
                comprador: document.getElementById('comprador').value,
                telefono: document.getElementById('telefono').value,
                categoria: document.getElementById('categoria').value,
                producto: document.getElementById('producto').value,
                presupuesto_max: parseFloat(document.getElementById('presupuesto').value),
                descripcion: document.getElementById('descripcion').value
            };
            await fetch('/publicar_busqueda', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify(datos) });
            document.getElementById('formGanga').reset();
            cargar();
        });
        cargar();
    </script>
</body>
</html>
"""

@app.route('/')
def inicio():
    db.session.add(Visita())
    db.session.commit()
    return render_template_string(HTML_TEMPLATE)

@app.route('/publicar_busqueda', methods=['POST'])
def publicar_busqueda():
    db.session.add(AnuncioBusqueda(**request.get_json()))
    db.session.commit()
    return jsonify({"mensaje": "OK"}), 201

@app.route('/ver_busquedas')
def ver_busquedas():
    anuncios = AnuncioBusqueda.query.order_by(AnuncioBusqueda.fecha_publicacion.desc()).all()
    return jsonify([{k: v for k, v in a.__dict__.items() if k != '_sa_instance_state'} for a in anuncios])

if __name__ == '__main__':
    app.run()
