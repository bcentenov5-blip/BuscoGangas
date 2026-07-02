from flask import Flask, request, jsonify, render_template_string
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///buscogangas.db'
app.config['TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Base de datos actualizada con el campo 'categoria'
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

# Interfaz gráfica de nueva generación con Filtros y Buscador
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BuscoGangas.shop | Panel de Control Ancestral</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-slate-900 text-slate-100 font-sans min-h-screen">
    <header class="border-b border-slate-800 bg-slate-950/50 backdrop-blur sticky top-0 z-50">
        <div class="max-w-5xl mx-auto px-4 py-4 flex justify-between items-center">
            <h1 class="text-2xl font-black tracking-wider text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400">
                BUSCO<span class="text-white">GANGAS</span>.shop
            </h1>
            <span class="bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-3 py-1 rounded-full text-xs font-mono font-bold uppercase tracking-widest">
                V1.2 • Filtros Activos
            </span>
        </div>
    </header>

    <main class="max-w-5xl mx-auto px-4 py-8 grid grid-cols-1 md:grid-cols-3 gap-8">
        
        <section class="md:col-span-1">
            <div class="bg-slate-950 border border-slate-800 p-6 rounded-2xl shadow-xl sticky top-24">
                <h2 class="text-xl font-bold text-white mb-1">🚀 Publicar Búsqueda</h2>
                <p class="text-xs text-slate-400 mb-6">Inyecta tu necesidad al mercado.</p>
                
                <form id="formGanga" class="space-y-4">
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Tu Nombre</label>
                        <input type="text" id="comprador" required placeholder="Ej: Diego Zúñiga" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">WhatsApp</label>
                        <input type="tel" id="telefono" required placeholder="Ej: 50688888888" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm font-mono">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Categoría</label>
                        <select id="categoria" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white focus:outline-none focus:border-cyan-500 text-sm">
                            <option value="Tecnología">💻 Tecnología / Componentes</option>
                            <option value="Videojuegos">🎮 Consolas y Juegos</option>
                            <option value="Ropa">👕 Ropa y Calzado</option>
                            <option value="Hogar">🏠 Artículos del Hogar</option>
                            <option value="Otros">📦 Otros / Curiosidades</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">¿Qué producto buscas?</label>
                        <input type="text" id="producto" required placeholder="Ej: Grafica RTX 3060" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Presupuesto Máximo</label>
                        <input type="number" id="presupuesto" required placeholder="Ej: 140000" class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm font-mono">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-slate-400 uppercase tracking-wider mb-1">Detalles</label>
                        <textarea id="descripcion" rows="2" placeholder="Detalles de lo que buscas..." class="w-full bg-slate-900 border border-slate-800 rounded-xl px-4 py-2.5 text-white placeholder-slate-600 focus:outline-none focus:border-cyan-500 text-sm resize-none"></textarea>
                    </div>
                    
                    <button type="submit" class="w-full bg-gradient-to-r from-cyan-500 to-emerald-500 text-slate-950 font-bold py-3 px-4 rounded-xl shadow-lg text-sm uppercase tracking-wider">
                        Publicar Demanda 📢
                    </button>
                </form>
            </div>
        </section>

        <section class="md:col-span-2 space-y-4">
            <div class="bg-slate-950 border border-slate-800 p-4 rounded-2xl flex flex-col sm:flex-row gap-3">
                <input type="text" id="buscador" oninput="filtrarAnuncios()" placeholder="🔍 ¿Qué buscas vender? Escribe aquí para buscar..." 
                       class="flex-1 bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 text-sm">
                
                <select id="filtroCategoria" onchange="filtrarAnuncios()" class="bg-slate-900 border border-slate-800 rounded-xl px-4 py-2 text-white focus:outline-none focus:border-cyan-500 text-sm">
                    <option value="TODAS">🌟 Todas las Categorías</option>
                    <option value="Tecnología">💻 Tecnología</option>
                    <option value="Videojuegos">🎮 Videojuegos</option>
                    <option value="Ropa">👕 Ropa</option>
                    <option value="Hogar">🏠 Hogar</option>
                    <option value="Otros">📦 Otros</option>
                </select>
            </div>
            
            <div id="contenedorAnuncios" class="space-y-4"></div>
        </section>

    </main>

    <script>
        let todosLosAnuncios = []; // Guardará los datos localmente para filtrar al instante

        async function cargarAnuncios() {
            const res = await fetch('/ver_busquedas');
            todosLosAnuncios = await res.json();
            filtrarAnuncios(); // Renderiza aplicando los filtros actuales
        }

        function filtrarAnuncios() {
            const textoBuscado = document.getElementById('buscador').value.toLowerCase();
            const categoriaSeleccionada = document.getElementById('filtroCategoria').value;
            const contenedor = document.getElementById('contenedorAnuncios');
            contenedor.innerHTML = '';

            const filtrados = todosLosAnuncios.filter(a => {
                const coincideTexto = a.producto.toLowerCase().includes(textoBuscado) || a.descripcion.toLowerCase().includes(textoBuscado);
                const coincideCat = (categoriaSeleccionada === "TODAS") || (a.categoria === categoriaSeleccionada);
                return coincideTexto && coincideCat;
            });

            if (filtrados.length === 0) {
                contenedor.innerHTML = `<div class="border border-dashed border-slate-800 rounded-2xl p-12 text-center text-slate-500 text-sm">Ninguna ganga coincide con tus filtros.</div>`;
                return;
            }

            filtrados.forEach(a => {
                const textoWhatsApp = encodeURIComponent(`¡Hola ${a.comprador}! Vi en BuscoGangas.shop que buscas un "${a.producto}" por ₡${a.presupuesto_max.toLocaleString('es-CR')}. Yo tengo uno disponible. ¿Hablamos?`);
                const enlaceWhatsApp = `https://wa.me/${a.telefono}?text=${textoWhatsApp}`;

                contenedor.innerHTML += `
                    <div class="bg-slate-950 border border-slate-800 p-5 rounded-2xl relative overflow-hidden">
                        <div class="absolute top-0 left-0 w-1 h-full bg-cyan-500"></div>
                        <div class="flex justify-between items-start gap-4 mb-2">
                            <div>
                                <span class="text-[10px] uppercase font-mono font-bold tracking-wider text-cyan-400 bg-cyan-500/10 px-2 py-0.5 rounded border border-cyan-500/10">${a.categoria}</span>
                                <h3 class="text-lg font-bold text-white mt-1">${a.producto}</h3>
                            </div>
                            <span class="text-xs font-mono font-bold text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded border border-emerald-500/20">
                                Max: ₡${a.presupuesto_max.toLocaleString('es-CR')}
                            </span>
                        </div>
                        <p class="text-sm text-slate-400 mb-4 bg-slate-900/50 p-3 rounded-xl border border-slate-900">${a.descripcion || 'Sin descripción.'}</p>
                        <div class="flex items-center justify-between pt-2 border-t border-slate-900 text-xs">
                            <span class="text-slate-400">Por: <strong class="text-slate-200">${a.comprador}</strong></span>
                            <a href="${enlaceWhatsApp}" target="_blank" class="bg-emerald-500 hover:bg-emerald-600 text-slate-950 font-bold px-4 py-2 rounded-xl transition-all flex items-center gap-1.5 uppercase tracking-wide">
                                🟢 YO LO TENGO
                            </a>
                        </div>
                    </div>
                `;
            });
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

            const res = await fetch('/publicar_busqueda', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(datos)
            });

            if (res.ok) {
                document.getElementById('formGanga').reset();
                cargarAnuncios();
            }
        });

        cargarAnuncios();
    </script>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def inicio():
    # Registrar visita
    nueva_visita = Visita()
    db.session.add(nueva_visita)
    db.session.commit()
    return render_template_string(HTML_TEMPLATE)

@app.route('/contador')
def ver_contador():
    total_visitas = Visita.query.count()
    return f"<h1>Total de visitas: {total_visitas}</h1>"

@app.route('/publicar_busqueda', methods=['POST'])
def publicar_busqueda():
    data = request.get_json()
    nuevo_anuncio = AnuncioBusqueda(
        comprador=data['comprador'],
        telefono=data['telefono'],
        categoria=data['categoria'],
        producto=data['producto'],
        presupuesto_max=data['presupuesto_max'],
        descripcion=data.get('descripcion', '')
    )
    db.session.add(nuevo_anuncio)
    db.session.commit()
    return jsonify({"mensaje": "¡Publicado!"}), 201

@app.route('/ver_busquedas', methods=['GET'])
def ver_busquedas():
    anuncios = AnuncioBusqueda.query.order_by(AnuncioBusqueda.fecha_publicacion.desc()).all()
    resultado = []
    for a in anuncios:
        resultado.append({
            "id": a.id,
            "comprador": a.comprador,
            "telefono": a.telefono,
            "categoria": a.categoria,
            "producto": a.producto,
            "presupuesto_max": a.presupuesto_max,
            "descripcion": a.descripcion,
            "fecha": a.fecha_publicacion.strftime('%Y-%m-%d %H:%M')
        })
    return jsonify(resultado), 200

if __name__ == '__main__':
    app.run(debug=True)
