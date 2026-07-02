from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buscogangas.db'
app.config['TRACK_MODIFICATIONS'] = False
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
    <meta name="description" content="BuscoGangas.shop: El lugar para encontrar compradores y vendedores de tecnología, juegos y artículos del hogar en Costa Rica.">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuscoGangas.shop | El mercado de ofertas en Costa Rica</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen">
    <header class="border-b border-slate-800 bg-slate-950/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">
                BUSCO<span class="text-white">GANGAS</span>.shop
            </h1>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        <section class="md:col-span-1">
            <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl shadow-xl sticky top-24">
                <h2 class="text-xl font-bold text-white mb-1">🚀 Publicar Búsqueda</h2>
                <form id="formGanga" class="space-y-4">
                    <input type="text" id="comprador" required placeholder="Tu Nombre" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm">
                    <input type="tel" id="telefono" required placeholder="WhatsApp" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm font-mono">
                    <select id="categoria" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm">
                        <option value="Tecnología">💻 Tecnología</option>
                        <option value="Videojuegos">🎮 Videojuegos</option>
                        <option value="Ropa">👕 Ropa</option>
                        <option value="Hogar">🏠 Hogar</option>
                        <option value="Otros">📦 Otros</option>
                    </select>
                    <input type="text" id="producto" required placeholder="Producto" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm">
                    <input type="number" id="presupuesto" required placeholder="Presupuesto" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm font-mono">
                    <textarea id="descripcion" rows="2" placeholder="Detalles..." class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm resize-none"></textarea>
                    <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold py-3 px-4 rounded-xl shadow-lg text-sm uppercase">Publicar</button>
                </form>
            </div>
        </section>

        <section class="md:col-span-2 space-y-4">
            <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl mb-8">
                <h3 class="text-sm font-bold text-slate-400 uppercase mb-4">🔥 Tendencias:</h3>
                <div id="listaTendencias" class="flex flex-wrap gap-2"></div>
            </div>
            <div class="bg-slate-950 border border-slate-800 p-4 rounded-2xl flex gap-3">
                <input type="text" id="buscador" oninput="filtrarAnuncios()" placeholder="🔍 Buscar..." class="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-white text-sm">
                <select id="filtroCategoria" onchange="filtrarAnuncios()" class="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-white text-sm">
                    <option value="TODAS">🌟 Todas</option>
                    <option value="Tecnología">💻 Tecnología</option>
                    <option value="Videojuegos">🎮 Videojuegos</option>
                    <option value="Ropa">👕 Ropa</option>
                    <option value="Hogar">🏠 Hogar</option>
                </select>
            </div>
            <div id="contenedorAnuncios" class="space-y-4"></div>
        </section>
    </main>

    <script>
        let todosLosAnuncios = [];
        async function cargarDatos() {
            const [resA, resT] = await Promise.all([fetch('/ver_busquedas'), fetch('/mas_buscados')]);
            todosLosAnuncios = await resA.json();
            const tendencias = await resT.json();
            document.getElementById('listaTendencias').innerHTML = tendencias.map(t => `<span class="bg-slate-800 text-cyan-400 px-3 py-1 rounded-full text-xs">${t.producto}</span>`).join('');
            filtrarAnuncios();
        }
        function filtrarAnuncios() {
            const texto = document.getElementById('buscador').value.toLowerCase();
            const cat = document.getElementById('filtroCategoria').value;
            const cont = document.getElementById('contenedorAnuncios');
            const filtrados = todosLosAnuncios.filter(a => (a.producto.toLowerCase().includes(texto) || a.descripcion.toLowerCase().includes(texto)) && (cat === "TODAS" || a.categoria === cat));
            cont.innerHTML = filtrados.map(a => `
                <div class="bg-slate-950 border border-slate-800 p-5 rounded-2xl">
                    <h3 class="text-lg font-bold text-white">${a.producto}</h3>
                    <p class="text-sm text-slate-400 mb-3">${a.descripcion}</p>
                    <div class="flex justify-between items-center text-xs">
                        <span class="text-emerald-400 font-bold">₡${a.presupuesto_max.toLocaleString('es-CR')}</span>
                        <a href="https://wa.me/${a.telefono}" target="_blank" class="bg-emerald-500 text-slate-950 font-bold px-4 py-2 rounded-xl">🟢 YO LO TENGO</a>
                    </div>
                </div>
            `).join('');
        }
        document.getElementById('formGanga').addEventListener('submit', async (e) => {
            e.preventDefault();
            await fetch('/publicar_busqueda', { method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({ comprador: document.getElementById('comprador').value, telefono: document.getElementById('telefono').value, categoria: document.getElementById('categoria').value, producto: document.getElementById('producto').value, presupuesto_max: parseFloat(document.getElementById('presupuesto').value), descripcion: document.getElementById('descripcion').value }) });
            document.getElementById('formGanga').reset();
            cargarDatos();
        });
        cargarDatos();
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
    return jsonify([{k: v for k, v in a.__dict__.items() if k != '_sa_instance_state'} for a in AnuncioBusqueda.query.order_by(AnuncioBusqueda.fecha_publicacion.desc()).all()])

@app.route('/mas_buscados')
def mas_buscados():
    return jsonify([{"producto": a.producto} for a in AnuncioBusqueda.query.order_by(AnuncioBusqueda.id.desc()).limit(3).all()])

@app.route('/contador')
def ver_contador():
    return f"<h1>Total de visitas: {Visita.query.count()}</h1>"

if __name__ == '__main__':
    app.run(debug=True)
