from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

#configuracion de la base de datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///biblioteca.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Instanciamos SQLAlchemy como ORM
db = SQLAlchemy(app)

#  TABLA INTERMEDIA  relación N – M entre Libros y Genero

libro_genero = db.Table(
    'libro_genero',
    db.Column('libro_id',  db.Integer, db.ForeignKey('libros.id'),  primary_key=True),
    db.Column('genero_id', db.Integer, db.ForeignKey('generos.id'), primary_key=True)
)

# MODELOS
class Autor(db.Model):
    __tablename__ = 'autores'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    nacionalidad = db.Column(db.String(100))

    # Relación 1 – N un Autor tiene muchos Libros
    # cascade="all, delete-orphan"  elimina el autor, se eliminan sus libros
    libros = db.relationship('Libro', back_populates='autor', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Autor: {self.nombre} ({self.nacionalidad})>"
    
class Genero(db.Model):
    __tablename__ = 'generos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)

    # Relación N – M inversa un Genero tiene muchos Libros
    libros = db.relationship('Libro', secondary=libro_genero, back_populates='generos')

    def __repr__(self):
        return f"<Genero: {self.nombre}>"

class Libro(db.Model):
    __tablename__ = 'libros'

    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    anio = db.Column(db.Integer)
    
    autor_id = db.Column(db.Integer, db.ForeignKey('autores.id'), nullable=False)
    
    # Relaciones
    autor = db.relationship('Autor', back_populates='libros')
    generos = db.relationship('Genero', secondary=libro_genero, back_populates='libros')
    
    def __repr__(self):
        # Usamos autor_id para el repr y evitar errores de carga antes del commit
        return f"<Libro: {self.titulo} (ID Autor: {self.autor_id})>"


def init_db():
    with app.app_context():
        db.create_all()
        print("\nBase de datos creada satisfactoriamente")

def insertar_datos():
    with app.app_context():
       
        # Creacion de autores
        autor1 = Autor(nombre="Diana Canaviri", nacionalidad="Boliviana")
        autor2 = Autor(nombre="Vania Calle", nacionalidad="Argentina")
        autor3 = Autor(nombre="Carlos Gutierres", nacionalidad="Mexicano")
        autor4 = Autor(nombre="Pedro Ibañez", nacionalidad="Chilena")

        # Creacion de generos
        genero1 = Genero(nombre="Investigacion")
        genero2 = Genero(nombre="Big data")
        genero3 = Genero(nombre="Diseño de software")
        genero4 = Genero(nombre="Programacion")

        # Creacion de libros
        libro1 = Libro(titulo="Metodologia de la Investigación", anio=2022, autor=autor2)
        libro2 = Libro(titulo="Base de datos", anio=2003, autor=autor3)
        libro3 = Libro(titulo="Seguridad de datos", anio=2005, autor=autor2)
        libro4 = Libro(titulo="Programacion de software", anio=2020, autor=autor4)
        libro5 = Libro(titulo="Java para principiantes", anio=2021, autor=autor3)
        
        #Asignación N – M libros a generos
        libro1.generos.extend([genero1, genero2])
        libro2.generos.extend([genero1, genero2])
        libro3.generos.extend([genero1, genero2, genero4])
        libro4.generos.append(genero3) 
        libro5.generos.append(genero4) 

        # Guardamos todo en la sesión y confirmamos
        db.session.add_all([autor1, autor2, autor3, autor4, genero1, genero2, genero3, genero4, libro1, libro2, libro3, libro4, libro5])
        db.session.commit()
        print("\nDatos insertados satisfactoriamente")
        
def consultar_datos():
    with app.app_context():
        
        print("\n Listado de Autores y sus libros:")
        autores = Autor.query.all()
        for a in autores:
            print(f"\n  Autor: {a.nombre} - {a.nacionalidad}")
            if a.libros:
                for l in a.libros:
                    generos_str = ", ".join(g.nombre for g in l.generos)
                    print(f"{l.titulo} - año: {l.anio},  Géneros: {generos_str}")
            else:
                print("No hay libros registrados para este autor")
                
        print("\n Listado de Géneros y sus libros:")
        generos = Genero.query.all()
        for g in generos:
            print(f"\n  Género: {g.nombre}")
            if g.libros:
                for l in g.libros:
                    print(f"{l.titulo} - Autor: {l.autor.nombre}")
            else:
                print("No hay libros registrados para este género")
                
def actualizar_datos():
    with app.app_context():
        print("\n Actualizando el título del libro con id=4")
        libro = Libro.query.filter_by(id=4).first()
        if libro:
            print(f"  Antes : {libro}")
            libro.titulo = "Programacion de software - Edición Revisada"
            libro.anio   = 2022
            db.session.commit()
            libro = Libro.query.filter_by(id=4).first()
            print("Libro ACTUALIZADO correctamente")
        else:
            print("Libro no encontrado")
            
def eliminar_datos():
    with app.app_context():
        print("\n Eliminando un autor con id=3")
        
        autor = Autor.query.filter_by(id=3).first()
        if autor:
            db.session.delete(autor)
            db.session.commit()
            print("Autor ELIMINADO correctamente")
        else:
            print("Autor no encontrado")
            
if __name__ == '__main__':
    init_db()
    insertar_datos()
    consultar_datos()
    actualizar_datos()
    consultar_datos()
    eliminar_datos()
    consultar_datos()