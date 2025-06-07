from sqlalchemy import create_engine, Column, Integer, String, Date, Enum, ForeignKey, Numeric, Text, TIMESTAMP, Table
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from sqlalchemy.exc import IntegrityError
from enum import Enum as PyEnum
from datetime import datetime
import os
import csv
from io import StringIO

# Configuración de la base de datos
DATABASE_URL = "postgresql://postgres:2604@localhost:5432/gaming_platform1"
# " postgressql://<usuario>:<contraseña>@<host>:<puerto(5432 por default)>/<nombre_base_datos>"
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()

# Tipos personalizados
class RolUsuario(PyEnum):
    JUGADOR = "JUGADOR"
    DESARROLLADOR = "DESARROLLADOR"

class EstadoJuego(PyEnum):
    BETA = "BETA"
    LANZADO = "LANZADO"
    RETIRADO = "RETIRADO"

class MetodoPago(PyEnum):
    TARJETA = "TARJETA"
    PAYPAL = "PAYPAL"
    CREDITO = "CREDITO"
    CRIPTO = "CRIPTO"

class TipoEvento(PyEnum):
    LANZAMIENTO = "LANZAMIENTO"
    TORNEO = "TORNEO"
    REBAJA = "REBAJA"

class Plataforma(PyEnum):
    WINDOWS = "WINDOWS"
    LINUX = "LINUX"
    MAC = "MAC"
    ANDROID = "ANDROID"
    IOS = "IOS"

# Modelo Usuario
class Usuario(Base):
    __tablename__ = 'usuario'
    
    id_usuario = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    correo = Column(String(100), unique=True, nullable=False)
    contraseña = Column(Text, nullable=False)
    rol_usuario = Column(Enum(RolUsuario), nullable=False)
    fecha_registro = Column(Date, default=datetime.now().date())
    
    perfiles = relationship("PerfilUsuario", back_populates="usuario")
    juegos_desarrollados = relationship("Juego", back_populates="desarrollador")
    compras = relationship("Compra", back_populates="usuario")
    reseñas = relationship("Reseña", back_populates="usuario")
    logros = relationship("ProgresoUsuarioLogro", back_populates="usuario")
    juegos_favoritos = relationship("JuegoFavorito", back_populates="usuario")
    eventos_participados = relationship("ParticipacionEvento", back_populates="usuario")
    comentarios = relationship("Comentario", back_populates="usuario")
    actividades = relationship("BitacoraActividad", back_populates="usuario")
    
    def __repr__(self):
        return f"{self.nombre} ({self.rol_usuario.value})"

# Modelo PerfilUsuario
class PerfilUsuario(Base):
    __tablename__ = 'perfilusuario'
    
    id_perfil = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    avatar_url = Column(Text)
    pais = Column(String(50))
    biografia = Column(Text)
    fecha_nacimiento = Column(Date)
    
    usuario = relationship("Usuario", back_populates="perfiles")
    
    def __repr__(self):
        return f"Perfil de {self.usuario.nombre}"

# Tabla intermedia para relación muchos-a-muchos Juego-Categoria
juego_categoria = Table(
    'juegocategoria', Base.metadata,
    Column('id_juego', Integer, ForeignKey('juego.id_juego'), primary_key=True),
    Column('id_categoria', Integer, ForeignKey('categoria.id_categoria'), primary_key=True)
)

# Modelo Juego
class Juego(Base):
    __tablename__ = 'juego'
    
    id_juego = Column(Integer, primary_key=True)
    nombre = Column(String(100), nullable=False)
    descripcion = Column(Text)
    fecha_lanzamiento = Column(Date)
    precio = Column(Numeric(10, 2), nullable=False)
    estado_juego = Column(Enum(EstadoJuego), nullable=False)
    id_desarrollador = Column(Integer, ForeignKey('usuario.id_usuario'))
    
    desarrollador = relationship("Usuario", back_populates="juegos_desarrollados")
    versiones = relationship("VersionJuego", back_populates="juego")
    compras = relationship("Compra", back_populates="juego")
    reseñas = relationship("Reseña", back_populates="juego")
    logros = relationship("Logro", back_populates="juego")
    categorias = relationship("Categoria", secondary=juego_categoria, back_populates="juegos")
    plataformas = relationship("JuegoPlataforma", back_populates="juego")
    favoritos = relationship("JuegoFavorito", back_populates="juego")
    mantenimientos = relationship("MantenimientoJuego", back_populates="juego")
    historial_precios = relationship("HistorialPrecio", back_populates="juego")
    reportes = relationship("ReporteJuego", back_populates="juego")
    
    def __repr__(self):
        return f"{self.nombre} ({self.estado_juego.value})"

# Modelo VersionJuego
class VersionJuego(Base):
    __tablename__ = 'versionjuego'
    
    id_version = Column(Integer, primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    numero_version = Column(String(20))
    fecha_publicacion = Column(Date)
    notas_cambios = Column(Text)
    
    juego = relationship("Juego", back_populates="versiones")
    
    def __repr__(self):
        return f"v{self.numero_version} de {self.juego.nombre}"

# Modelo Compra
class Compra(Base):
    __tablename__ = 'compra'
    
    id_compra = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    fecha_compra = Column(TIMESTAMP, default=datetime.now())
    monto_pagado = Column(Numeric(10, 2))
    metodo_pago = Column(Enum(MetodoPago))
    
    usuario = relationship("Usuario", back_populates="compras")
    juego = relationship("Juego", back_populates="compras")
    
    def __repr__(self):
        return f"Compra #{self.id_compra} - {self.usuario.nombre} -> {self.juego.nombre}"

# Modelo Reseña
class Reseña(Base):
    __tablename__ = 'reseña'
    
    id_reseña = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    calificacion = Column(Integer)
    comentario = Column(Text)
    fecha_reseña = Column(Date)
    
    usuario = relationship("Usuario", back_populates="reseñas")
    juego = relationship("Juego", back_populates="reseñas")
    
    def __repr__(self):
        return f"Reseña de {self.usuario.nombre} para {self.juego.nombre}"

# Modelo Logro
class Logro(Base):
    __tablename__ = 'logro'
    
    id_logro = Column(Integer, primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    nombre = Column(String(100))
    descripcion = Column(Text)
    puntos = Column(Integer)
    
    juego = relationship("Juego", back_populates="logros")
    usuarios = relationship("ProgresoUsuarioLogro", back_populates="logro")
    
    def __repr__(self):
        return f"{self.nombre} ({self.puntos} pts)"

# Modelo ProgresoUsuarioLogro
class ProgresoUsuarioLogro(Base):
    __tablename__ = 'progresousuariologro'
    
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), primary_key=True)
    id_logro = Column(Integer, ForeignKey('logro.id_logro'), primary_key=True)
    fecha_desbloqueo = Column(Date)
    
    usuario = relationship("Usuario", back_populates="logros")
    logro = relationship("Logro", back_populates="usuarios")
    
    def __repr__(self):
        return f"{self.usuario.nombre} desbloqueó {self.logro.nombre}"

# Modelo Categoria
class Categoria(Base):
    __tablename__ = 'categoria'
    
    id_categoria = Column(Integer, primary_key=True)
    nombre = Column(String(50), nullable=False)
    
    juegos = relationship("Juego", secondary=juego_categoria, back_populates="categorias")
    
    def __repr__(self):
        return self.nombre

# Modelo JuegoPlataforma
class JuegoPlataforma(Base):
    __tablename__ = 'juegoplataforma'
    
    id_juego = Column(Integer, ForeignKey('juego.id_juego'), primary_key=True)
    plataforma = Column(Enum(Plataforma), primary_key=True)
    
    juego = relationship("Juego", back_populates="plataformas")
    
    def __repr__(self):
        return f"{self.juego.nombre} en {self.plataforma.value}"

# Modelo JuegoFavorito
class JuegoFavorito(Base):
    __tablename__ = 'juegofavorito'
    
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'), primary_key=True)
    fecha_marcado = Column(Date)
    
    usuario = relationship("Usuario", back_populates="juegos_favoritos")
    juego = relationship("Juego", back_populates="favoritos")
    
    def __repr__(self):
        return f"{self.usuario.nombre} -> {self.juego.nombre}"

# Modelo Evento
class Evento(Base):
    __tablename__ = 'evento'
    
    id_evento = Column(Integer, primary_key=True)
    titulo = Column(String(100))
    descripcion = Column(Text)
    fecha_inicio = Column(Date)
    fecha_fin = Column(Date)
    tipo_evento = Column(Enum(TipoEvento))
    
    participantes = relationship("ParticipacionEvento", back_populates="evento")
    comentarios = relationship("Comentario", back_populates="evento")  # Ensure this relationship exists
    
    def __repr__(self):
        return f"{self.titulo} ({self.tipo_evento.value})"

# Modelo ParticipacionEvento
class ParticipacionEvento(Base):
    __tablename__ = 'participacionevento'
    
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'), primary_key=True)
    id_evento = Column(Integer, ForeignKey('evento.id_evento'), primary_key=True)
    fecha_inscripcion = Column(Date)
    
    usuario = relationship("Usuario", back_populates="eventos_participados")
    evento = relationship("Evento", back_populates="participantes")
    
    def __repr__(self):
        return f"{self.usuario.nombre} en {self.evento.titulo}"

# Modelo Comentario
class Comentario(Base):
    __tablename__ = 'comentario'
    
    id_comentario = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    id_evento = Column(Integer, ForeignKey('evento.id_evento'))  # Add this foreign key
    tipo_objetivo = Column(String(20))  # Simplificado para el ejemplo
    id_objetivo = Column(Integer)
    contenido = Column(Text)
    fecha = Column(TIMESTAMP, default=datetime.now())
    
    usuario = relationship("Usuario", back_populates="comentarios")
    evento = relationship("Evento", back_populates="comentarios")  # Add this relationship
    reportes = relationship("ReporteComentario", back_populates="comentario")
    
    def __repr__(self):
        return f"Comentario de {self.usuario.nombre}"

# Modelo ReporteComentario
class ReporteComentario(Base):
    __tablename__ = 'reportecomentario'
    
    id_reporte = Column(Integer, primary_key=True)
    id_comentario = Column(Integer, ForeignKey('comentario.id_comentario'))
    motivo = Column(Text)
    fecha_reporte = Column(Date, default=datetime.now().date())
    
    comentario = relationship("Comentario", back_populates="reportes")
    
    def __repr__(self):
        return f"Reporte #{self.id_reporte}"

# Modelo BitacoraActividad
class BitacoraActividad(Base):
    __tablename__ = 'bitacoraactividad'
    
    id_actividad = Column(Integer, primary_key=True)
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    tipo_actividad = Column(String(50))
    descripcion = Column(Text)
    fecha = Column(TIMESTAMP, default=datetime.now())
    
    usuario = relationship("Usuario", back_populates="actividades")
    
    def __repr__(self):
        return f"{self.tipo_actividad} - {self.usuario.nombre}"

# Modelo MantenimientoJuego
class MantenimientoJuego(Base):
    __tablename__ = 'mantenimientojuego'
    
    id_mantenimiento = Column(Integer, primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    fecha_inicio = Column(TIMESTAMP)
    fecha_fin = Column(TIMESTAMP)
    motivo = Column(Text)
    
    juego = relationship("Juego", back_populates="mantenimientos")
    
    def __repr__(self):
        return f"Mantenimiento de {self.juego.nombre}"

# Modelo HistorialPrecio
class HistorialPrecio(Base):
    __tablename__ = 'historialprecio'
    
    id_historial = Column(Integer, primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    precio_anterior = Column(Numeric(10, 2))
    precio_nuevo = Column(Numeric(10, 2))
    fecha_cambio = Column(Date)
    
    juego = relationship("Juego", back_populates="historial_precios")
    
    def __repr__(self):
        return f"Cambio de precio {self.precio_anterior} -> {self.precio_nuevo}"

# Modelo ReporteJuego
class ReporteJuego(Base):
    __tablename__ = 'reportejuego'
    
    id_reporte = Column(Integer, primary_key=True)
    id_juego = Column(Integer, ForeignKey('juego.id_juego'))
    id_usuario = Column(Integer, ForeignKey('usuario.id_usuario'))
    motivo = Column(Text)
    fecha_reporte = Column(Date, default=datetime.now().date())
    
    juego = relationship("Juego", back_populates="reportes")
    usuario = relationship("Usuario")
    
    def __repr__(self):
        return f"Reporte #{self.id_reporte}"

# Crear tablas si no existen
Base.metadata.create_all(engine)

# Funciones auxiliares
def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def mostrar_menu_principal():
    limpiar_pantalla()
    print("""
    SISTEMA DE GESTIÓN DE PLATAFORMA DE JUEGOS
    ------------------------------------------
    1. Gestión de Usuarios
    2. Gestión de Juegos
    3. Gestión de Eventos
    4. Reportes y Estadísticas
    5. Salir
    """)

def mostrar_menu_usuarios():
    limpiar_pantalla()
    print("""
    GESTIÓN DE USUARIOS
    -------------------
    1. Listar todos los usuarios
    2. Agregar nuevo usuario
    3. Editar usuario existente
    4. Eliminar usuario
    5. Ver perfil de usuario
    6. Volver al menú principal
    """)

def mostrar_menu_juegos():
    limpiar_pantalla()
    print("""
    GESTIÓN DE JUEGOS
    -----------------
    1. Listar todos los juegos
    2. Agregar nuevo juego
    3. Editar juego existente
    4. Eliminar juego
    5. Gestionar versiones de juego
    6. Volver al menú principal
    """)

def mostrar_menu_eventos():
    limpiar_pantalla()
    print("""
    GESTIÓN DE EVENTOS
    ------------------
    1. Listar todos los eventos
    2. Agregar nuevo evento
    3. Editar evento existente
    4. Eliminar evento
    5. Gestionar participantes
    6. Volver al menú principal
    """)

def listar_eventos():
    eventos = session.query(Evento).order_by(Evento.fecha_inicio.desc()).all()
    print("\nLISTADO DE EVENTOS:")
    print("-" * 80)
    for evento in eventos:
        print(f"ID: {evento.id_evento}")
        print(f"Título: {evento.titulo}")
        print(f"Descripción: {evento.descripcion}")
        print(f"Fecha inicio: {evento.fecha_inicio}")
        print(f"Fecha fin: {evento.fecha_fin}")
        print(f"Tipo: {evento.tipo_evento.value}")
        print("-" * 80)
    input("\nPresione Enter para continuar...")

def agregar_evento():
    print("\nAGREGAR NUEVO EVENTO")
    print("-" * 30)
    titulo = input("Título del evento: ")
    descripcion = input("Descripción: ")
    fecha_inicio = input("Fecha de inicio (YYYY-MM-DD): ")
    fecha_fin = input("Fecha de fin (YYYY-MM-DD): ")
    print("\nTipos de evento disponibles:")
    for i, tipo in enumerate(TipoEvento, 1):
        print(f"{i}. {tipo.value}")
    tipo_opcion = int(input("Seleccione el tipo de evento: "))
    tipo = list(TipoEvento)[tipo_opcion - 1]
    try:
        evento = Evento(
            titulo=titulo,
            descripcion=descripcion,
            fecha_inicio=datetime.strptime(fecha_inicio, "%Y-%m-%d").date(),
            fecha_fin=datetime.strptime(fecha_fin, "%Y-%m-%d").date(),
            tipo_evento=tipo
        )
        session.add(evento)
        session.commit()
        print("\n¡Evento agregado exitosamente!")
    except Exception as e:
        session.rollback()
        print(f"\nError: {str(e)}")
    input("Presione Enter para continuar...")

def mostrar_menu_reportes():
    limpiar_pantalla()
    print("""
    REPORTES Y ESTADÍSTICAS
    -----------------------
    1. Reporte de ventas
    2. Reporte de reseñas
    3. Reporte de actividad de usuarios
    4. Exportar datos a CSV
    5. Volver al menú principal
    """)

def listar_usuarios():
    usuarios = session.query(Usuario).order_by(Usuario.nombre).all()
    print("\nLISTADO DE USUARIOS:")
    print("-" * 80)
    for usuario in usuarios:
        print(f"ID: {usuario.id_usuario}")
        print(f"Nombre: {usuario.nombre}")
        print(f"Correo: {usuario.correo}")
        print(f"Rol: {usuario.rol_usuario.value}")
        print(f"Fecha registro: {usuario.fecha_registro}")
        print("-" * 80)
    input("\nPresione Enter para continuar...")

def agregar_usuario():
    print("\nAGREGAR NUEVO USUARIO")
    print("-" * 30)
    
    nombre = input("Nombre: ")
    correo = input("Correo electrónico: ")
    contraseña = input("Contraseña: ")
    
    print("\nRoles disponibles:")
    for i, rol in enumerate(RolUsuario, 1):
        print(f"{i}. {rol.value}")
    rol_opcion = int(input("Seleccione el rol: "))
    rol = list(RolUsuario)[rol_opcion - 1]
    
    try:
        usuario = Usuario(
            nombre=nombre,
            correo=correo,
            contraseña=contraseña,
            rol_usuario=rol
        )
        
        session.add(usuario)
        session.commit()
        
        # Crear perfil básico
        perfil = PerfilUsuario(
            id_usuario=usuario.id_usuario,
            pais="",
            biografia=""
        )
        session.add(perfil)
        session.commit()
        
        print("\n¡Usuario agregado exitosamente!")
    except IntegrityError:
        session.rollback()
        print("\nError: El correo electrónico ya está en uso.")
    except Exception as e:
        session.rollback()
        print(f"\nError: {str(e)}")
    
    input("Presione Enter para continuar...")

def editar_usuario():
    listar_usuarios()
    usuario_id = int(input("\nIngrese el ID del usuario a editar: "))
    usuario = session.query(Usuario).get(usuario_id)
    
    if not usuario:
        print("Usuario no encontrado.")
        input("Presione Enter para continuar...")
        return
    
    print(f"\nEditando usuario: {usuario.nombre}")
    print("(Deje en blanco para mantener el valor actual)")
    
    nombre = input(f"Nuevo nombre [{usuario.nombre}]: ") or usuario.nombre
    correo = input(f"Nuevo correo [{usuario.correo}]: ") or usuario.correo
    
    print(f"\nRol actual: {usuario.rol_usuario.value}")
    if input("¿Cambiar rol? (s/n): ").lower() == 's':
        print("\nRoles disponibles:")
        for i, rol in enumerate(RolUsuario, 1):
            print(f"{i}. {rol.value}")
        rol_opcion = int(input("Seleccione el nuevo rol: "))
        rol = list(RolUsuario)[rol_opcion - 1]
    else:
        rol = usuario.rol_usuario
    
    try:
        usuario.nombre = nombre
        usuario.correo = correo
        usuario.rol_usuario = rol
        
        session.commit()
        print("\n¡Usuario actualizado exitosamente!")
    except IntegrityError:
        session.rollback()
        print("\nError: El correo electrónico ya está en uso.")
    except Exception as e:
        session.rollback()
        print(f"\nError: {str(e)}")
    
    input("Presione Enter para continuar...")

def eliminar_usuario():
    listar_usuarios()
    usuario_id = int(input("\nIngrese el ID del usuario a eliminar: "))
    usuario = session.query(Usuario).get(usuario_id)
    
    if not usuario:
        print("Usuario no encontrado.")
        input("Presione Enter para continuar...")
        return
    
    # Verificar relaciones
    if usuario.juegos_desarrollados or usuario.compras or usuario.reseñas:
        print("\nEste usuario tiene registros asociados (juegos, compras o reseñas).")
        print("No se puede eliminar para mantener la integridad de los datos.")
        input("Presione Enter para continuar...")
        return
    
    confirmacion = input(f"\n¿Está seguro de eliminar a '{usuario.nombre}'? (s/n): ")
    if confirmacion.lower() == 's':
        try:
            # Eliminar perfil primero si existe
            perfil = session.query(PerfilUsuario).filter_by(id_usuario=usuario.id_usuario).first()
            if perfil:
                session.delete(perfil)
            
            session.delete(usuario)
            session.commit()
            print("\n¡Usuario eliminado exitosamente!")
        except Exception as e:
            session.rollback()
            print(f"\nError: {str(e)}")
    
    input("Presione Enter para continuar...")

def ver_perfil_usuario():
    listar_usuarios()
    usuario_id = int(input("\nIngrese el ID del usuario para ver su perfil: "))
    usuario = session.query(Usuario).get(usuario_id)
    
    if not usuario:
        print("Usuario no encontrado.")
        input("Presione Enter para continuar...")
        return
    
    perfil = session.query(PerfilUsuario).filter_by(id_usuario=usuario.id_usuario).first()
    
    print(f"\nPERFIL DE {usuario.nombre.upper()}")
    print("-" * 80)
    print(f"Rol: {usuario.rol_usuario.value}")
    print(f"Correo: {usuario.correo}")
    print(f"Fecha registro: {usuario.fecha_registro}")
    
    if perfil:
        print("\nINFORMACIÓN DEL PERFIL:")
        print(f"País: {perfil.pais}")
        print(f"Biografía: {perfil.biografia}")
        print(f"Fecha nacimiento: {perfil.fecha_nacimiento}")
        if perfil.avatar_url:
            print(f"Avatar: {perfil.avatar_url}")
    else:
        print("\nEste usuario no tiene perfil creado.")
    
    input("\nPresione Enter para continuar...")

def listar_juegos():
    juegos = session.query(Juego).order_by(Juego.nombre).all()
    print("\nLISTADO DE JUEGOS:")
    print("-" * 80)
    for juego in juegos:
        print(f"ID: {juego.id_juego}")
        print(f"Nombre: {juego.nombre}")
        print(f"Desarrollador: {juego.desarrollador.nombre if juego.desarrollador else 'N/A'}")
        print(f"Precio: ${juego.precio:.2f}")
        print(f"Estado: {juego.estado_juego.value}")
        print(f"Lanzamiento: {juego.fecha_lanzamiento}")
        print("-" * 80)
    input("\nPresione Enter para continuar...")

def agregar_juego():
    print("\nAGREGAR NUEVO JUEGO")
    print("-" * 30)
    nombre = input("Nombre del juego: ")
    descripcion = input("Descripción: ")
    fecha_lanzamiento = input("Fecha de lanzamiento (YYYY-MM-DD): ")
    precio = float(input("Precio: $"))
    print("\nEstados disponibles:")
    for i, estado in enumerate(EstadoJuego, 1):
        print(f"{i}. {estado.value}")
    estado_opcion = int(input("Seleccione el estado: "))
    estado = list(EstadoJuego)[estado_opcion - 1]
    desarrolladores = session.query(Usuario).filter_by(rol_usuario=RolUsuario.DESARROLLADOR).all()
    if not desarrolladores:
        print("\nNo hay desarrolladores registrados. Debe crear al menos uno primero.")
        input("Presione Enter para continuar...")
        return
    print("\nDesarrolladores disponibles:")
    for i, dev in enumerate(desarrolladores, 1):
        print(f"{i}. {dev.nombre}")
    dev_opcion = int(input("Seleccione el desarrollador: "))
    desarrollador = desarrolladores[dev_opcion - 1]
    try:
        juego = Juego(
            nombre=nombre,
            descripcion=descripcion,
            fecha_lanzamiento=datetime.strptime(fecha_lanzamiento, "%Y-%m-%d").date(),
            precio=precio,
            estado_juego=estado,
            id_desarrollador=desarrollador.id_usuario
        )
        session.add(juego)
        session.commit()
        version = VersionJuego(
            id_juego=juego.id_juego,
            numero_version="1.0",
            fecha_publicacion=datetime.now().date(),
            notas_cambios="Versión inicial"
        )
        session.add(version)
        session.commit()
        print("\n¡Juego agregado exitosamente!")
    except Exception as e:
        session.rollback()
        print(f"\nError: {str(e)}")
    input("Presione Enter para continuar...")

# === NUEVAS FUNCIONES DE GESTIÓN ===
def editar_juego():
    listar_juegos()
    juego_id = input("\nIngrese el ID del juego a editar: ")
    juego = session.query(Juego).get(juego_id)
    if not juego:
        print("Juego no encontrado.")
        input("Presione Enter para continuar...")
        return
    print(f"\nEditando juego: {juego.nombre}")
    print("(Deje en blanco para mantener el valor actual)")
    nombre = input(f"Nuevo nombre [{juego.nombre}]: ") or juego.nombre
    descripcion = input(f"Nueva descripción [{juego.descripcion}]: ") or juego.descripcion
    fecha_lanzamiento = input(f"Nueva fecha de lanzamiento [{juego.fecha_lanzamiento}]: ") or str(juego.fecha_lanzamiento)
    precio = input(f"Nuevo precio [{juego.precio}]: ") or str(juego.precio)
    print(f"\nEstado actual: {juego.estado_juego.value}")
    if input("¿Cambiar estado? (s/n): ").lower() == 's':
        for i, estado in enumerate(EstadoJuego, 1):
            print(f"{i}. {estado.value}")
        estado_opcion = int(input("Seleccione el nuevo estado: "))
        estado = list(EstadoJuego)[estado_opcion - 1]
    else:
        estado = juego.estado_juego
    desarrolladores = session.query(Usuario).filter_by(rol_usuario=RolUsuario.DESARROLLADOR).all()
    print(f"\nDesarrollador actual: {juego.desarrollador.nombre if juego.desarrollador else 'N/A'}")
    if input("¿Cambiar desarrollador? (s/n): ").lower() == 's':
        for i, dev in enumerate(desarrolladores, 1):
            print(f"{i}. {dev.nombre}")
        dev_opcion = int(input("Seleccione el nuevo desarrollador: "))
        desarrollador = desarrolladores[dev_opcion - 1]
        id_desarrollador = desarrollador.id_usuario
    else:
        id_desarrollador = juego.id_desarrollador
    try:
        juego.nombre = nombre
        juego.descripcion = descripcion
        juego.fecha_lanzamiento = datetime.strptime(fecha_lanzamiento, "%Y-%m-%d").date()
        juego.precio = float(precio)
        juego.estado_juego = estado
        juego.id_desarrollador = id_desarrollador
        session.commit()
        print("\n¡Juego actualizado exitosamente!")
    except Exception as e:
        session.rollback()
        print(f"\nError: {str(e)}")
    input("Presione Enter para continuar...")

def gestionar_versiones():
    listar_juegos()
    juego_id = input("\nIngrese el ID del juego para gestionar versiones: ")
    juego = session.query(Juego).get(juego_id)
    if not juego:
        print("Juego no encontrado.")
        input("Presione Enter para continuar...")
        return
    while True:
        limpiar_pantalla()
        print(f"GESTIÓN DE VERSIONES DE: {juego.nombre}")
        print("-" * 40)
        versiones = session.query(VersionJuego).filter_by(id_juego=juego.id_juego).order_by(VersionJuego.fecha_publicacion.desc()).all()
        for v in versiones:
            print(f"ID: {v.id_version} | Versión: {v.numero_version} | Fecha: {v.fecha_publicacion} | Notas: {v.notas_cambios}")
        print("\n1. Agregar nueva versión")
        print("2. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            numero_version = input("Número de versión (ej: 1.1, 2.0): ")
            fecha_publicacion = input("Fecha de publicación (YYYY-MM-DD): ")
            notas_cambios = input("Notas de cambios: ")
            try:
                version = VersionJuego(
                    id_juego=juego.id_juego,
                    numero_version=numero_version,
                    fecha_publicacion=datetime.strptime(fecha_publicacion, "%Y-%m-%d").date(),
                    notas_cambios=notas_cambios
                )
                session.add(version)
                session.commit()
                print("\n¡Versión agregada!")
            except Exception as e:
                session.rollback()
                print(f"Error: {str(e)}")
            input("Presione Enter para continuar...")
        elif op == "2":
            break
        else:
            print("Opción inválida.")
            input("Presione Enter para continuar...")

def gestionar_participantes():
    listar_eventos()
    evento_id = input("\nIngrese el ID del evento para gestionar participantes: ")
    evento = session.query(Evento).get(evento_id)
    if not evento:
        print("Evento no encontrado.")
        input("Presione Enter para continuar...")
        return
    while True:
        limpiar_pantalla()
        print(f"GESTIÓN DE PARTICIPANTES DE: {evento.titulo}")
        print("-" * 40)
        participantes = session.query(ParticipacionEvento).filter_by(id_evento=evento.id_evento).all()
        for p in participantes:
            print(f"Usuario: {p.usuario.nombre} | Fecha inscripción: {p.fecha_inscripcion}")
        print("\n1. Agregar participante")
        print("2. Volver")
        op = input("Seleccione una opción: ")
        if op == "1":
            usuarios = session.query(Usuario).all()
            for i, u in enumerate(usuarios, 1):
                print(f"{i}. {u.nombre}")
            user_op = int(input("Seleccione el usuario: "))
            usuario = usuarios[user_op - 1]
            if session.query(ParticipacionEvento).filter_by(id_usuario=usuario.id_usuario, id_evento=evento.id_evento).first():
                print("El usuario ya está inscrito en este evento.")
            else:
                try:
                    participacion = ParticipacionEvento(
                        id_usuario=usuario.id_usuario,
                        id_evento=evento.id_evento,
                        fecha_inscripcion=datetime.now().date()
                    )
                    session.add(participacion)
                    session.commit()
                    print("¡Participante agregado!")
                except Exception as e:
                    session.rollback()
                    print(f"Error: {str(e)}")
            input("Presione Enter para continuar...")
        elif op == "2":
            break
        else:
            print("Opción inválida.")
            input("Presione Enter para continuar...")


def reporte_ventas():
    print("\nREPORTE DE VENTAS")
    print("-" * 50)
    # Filtros
    fecha_inicio = input("Fecha inicio (YYYY-MM-DD, dejar vacío para omitir): ")
    fecha_fin = input("Fecha fin (YYYY-MM-DD, dejar vacío para omitir): ")
    print("\nMétodos de pago disponibles:")
    for i, metodo in enumerate(MetodoPago, 1):
        print(f"{i}. {metodo.value}")
    metodo_opcion = input("Seleccione método de pago (dejar vacío para todos): ")
    usuario_id = input("ID de usuario (dejar vacío para todos): ")
    juego_id = input("ID de juego (dejar vacío para todos): ")
    # Construir consulta
    query = session.query(
        Compra.id_compra,
        Usuario.nombre.label('usuario'),
        Juego.nombre.label('juego'),
        Compra.monto_pagado,
        Compra.fecha_compra,
        Compra.metodo_pago
    ).select_from(Compra).join(Usuario, Compra.id_usuario == Usuario.id_usuario).join(Juego, Compra.id_juego == Juego.id_juego)
    if fecha_inicio:
        try:
            fecha_inicio_dt = datetime.strptime(fecha_inicio, "%Y-%m-%d")
            query = query.filter(Compra.fecha_compra >= fecha_inicio_dt)
        except Exception:
            print("Fecha de inicio inválida. Se ignorará el filtro.")
    if fecha_fin:
        try:
            fecha_fin_dt = datetime.strptime(fecha_fin, "%Y-%m-%d")
            query = query.filter(Compra.fecha_compra <= fecha_fin_dt)
        except Exception:
            print("Fecha de fin inválida. Se ignorará el filtro.")
    if metodo_opcion:
        try:
            metodo = list(MetodoPago)[int(metodo_opcion) - 1]
            query = query.filter(Compra.metodo_pago == metodo)
        except Exception:
            print("Método de pago inválido. Se ignorará el filtro.")
    if usuario_id:
        try:
            query = query.filter(Compra.id_usuario == int(usuario_id))
        except Exception:
            print("ID de usuario inválido. Se ignorará el filtro.")
    if juego_id:
        try:
            query = query.filter(Compra.id_juego == int(juego_id))
        except Exception:
            print("ID de juego inválido. Se ignorará el filtro.")
    ventas = query.order_by(Compra.fecha_compra.desc()).all()
    if not ventas:
        print("\nNo se encontraron ventas con los filtros especificados.")
        input("Presione Enter para continuar...")
        return
    print("\nRESULTADOS:")
    print("-" * 120)
    print(f"{'ID':<5} | {'Usuario':<20} | {'Juego':<30} | {'Monto':<10} | {'Fecha':<20} | {'Método':<15}")
    print("-" * 120)
    for venta in ventas:
        print(f"{venta.id_compra:<5} | {venta.usuario:<20} | {venta.juego:<30} | ${venta.monto_pagado:<9.2f} | {venta.fecha_compra.strftime('%Y-%m-%d %H:%M'):<20} | {venta.metodo_pago.value:<15}")
    # Exportar a CSV
    if input("\n¿Exportar a CSV? (s/n): ").lower() == 's':
        output = StringIO()
        writer = csv.writer(output)
        writer.writerow(['ID', 'Usuario', 'Juego', 'Monto', 'Fecha', 'Método Pago'])
        for venta in ventas:
            writer.writerow([
                venta.id_compra,
                venta.usuario,
                venta.juego,
                venta.monto_pagado,
                venta.fecha_compra.strftime('%Y-%m-%d %H:%M'),
                venta.metodo_pago.value
            ])
        with open('reporte_ventas.csv', 'w', newline='', encoding='utf-8') as f:
            f.write(output.getvalue())
        print("\n¡Reporte exportado como 'reporte_ventas.csv'!")
    input("\nPresione Enter para continuar...")

def reporte_resenas():
    print("\nREPORTE DE RESEÑAS")
    print("-" * 50)
    juego_id = input("ID de juego (dejar vacío para todos): ")
    usuario_id = input("ID de usuario (dejar vacío para todos): ")
    query = session.query(
        Reseña.id_reseña,
        Usuario.nombre.label('usuario'),
        Juego.nombre.label('juego'),
        Reseña.calificacion,
        Reseña.comentario,
        Reseña.fecha_reseña
    ).select_from(Reseña).join(Usuario, Reseña.id_usuario == Usuario.id_usuario).join(Juego, Reseña.id_juego == Juego.id_juego)
    if juego_id:
        try:
            query = query.filter(Reseña.id_juego == int(juego_id))
        except Exception:
            print("ID de juego inválido. Se ignorará el filtro.")
    if usuario_id:
        try:
            query = query.filter(Reseña.id_usuario == int(usuario_id))
        except Exception:
            print("ID de usuario inválido. Se ignorará el filtro.")
    resenas = query.order_by(Reseña.fecha_reseña.desc()).all()
    if not resenas:
        print("\nNo se encontraron reseñas con los filtros especificados.")
        input("Presione Enter para continuar...")
        return
    print("\nRESULTADOS DE RESEÑAS:")
    print("-" * 80)
    for resena in resenas:
        print(f"ID Reseña: {resena.id_reseña}")
        print(f"Usuario: {resena.usuario}")
        print(f"Juego: {resena.juego}")
        print(f"Calificación: {resena.calificacion}")
        print(f"Comentario: {resena.comentario}")
        print(f"Fecha: {resena.fecha_reseña}")
        print("-" * 80)
    input("\nPresione Enter para continuar...")

def reporte_actividad_usuarios():
    print("\nREPORTE DE ACTIVIDAD DE USUARIOS")
    print("-" * 50)
    usuario_id = input("ID de usuario (dejar vacío para todos): ")
    tipo_actividad = input("Tipo de actividad (dejar vacío para todas): ")
    query = session.query(
        BitacoraActividad.id_actividad,
        Usuario.nombre.label('usuario'),
        BitacoraActividad.tipo_actividad,
        BitacoraActividad.descripcion,
        BitacoraActividad.fecha
    ).select_from(BitacoraActividad).join(Usuario, BitacoraActividad.id_usuario == Usuario.id_usuario)
    if usuario_id:
        try:
            query = query.filter(BitacoraActividad.id_usuario == int(usuario_id))
        except Exception:
            print("ID de usuario inválido. Se ignorará el filtro.")
    if tipo_actividad:
        query = query.filter(BitacoraActividad.tipo_actividad.ilike(f"%{tipo_actividad}%"))
    actividades = query.order_by(BitacoraActividad.fecha.desc()).all()
    if not actividades:
        print("\nNo se encontraron actividades con los filtros especificados.")
        input("Presione Enter para continuar...")
        return
    print("\nRESULTADOS DE ACTIVIDAD:")
    print("-" * 80)
    for act in actividades:
        print(f"ID Actividad: {act.id_actividad}")
        print(f"Usuario: {act.usuario}")
        print(f"Tipo: {act.tipo_actividad}")
        print(f"Descripción: {act.descripcion}")
        print(f"Fecha: {act.fecha}")
        print("-" * 80)
    input("\nPresione Enter para continuar...")

def exportar_datos_csv():
    print("\nEXPORTAR DATOS A CSV")
    print("-" * 50)
    tablas = [
        ("usuarios", Usuario),
        ("juegos", Juego),
        ("compras", Compra),
        ("reseñas", Reseña),
        ("eventos", Evento)
    ]
    for nombre, modelo in tablas:
        registros = session.query(modelo).all()
        if not registros:
            continue
        filename = f"{nombre}.csv"
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.writer(f)
            # Escribir encabezados
            writer.writerow([col.name for col in modelo.__table__.columns])
            for reg in registros:
                writer.writerow([getattr(reg, col.name) for col in modelo.__table__.columns])
        print(f"Exportado: {filename}")
    input("\nPresione Enter para continuar...")

# Menú principal
def main():
    while True:
        mostrar_menu_principal()
        opcion = input("Seleccione una opción: ")
        
        if opcion == "1":
            while True:
                mostrar_menu_usuarios()
                opcion_usuarios = input("Seleccione una opción: ")
                
                if opcion_usuarios == "1":
                    listar_usuarios()
                elif opcion_usuarios == "2":
                    agregar_usuario()
                elif opcion_usuarios == "3":
                    editar_usuario()
                elif opcion_usuarios == "4":
                    eliminar_usuario()
                elif opcion_usuarios == "5":
                    ver_perfil_usuario()
                elif opcion_usuarios == "6":
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
                    input("Presione Enter para continuar...")
        
        elif opcion == "2":
            while True:
                mostrar_menu_juegos()
                opcion_juegos = input("Seleccione una opción: ")
                
                if opcion_juegos == "1":
                    listar_juegos()
                elif opcion_juegos == "2":
                    agregar_juego()
                elif opcion_juegos == "3":
                    editar_juego()
                elif opcion_juegos == "4":
                    print("Función no implementada aún")
                    input("Presione Enter para continuar...")
                elif opcion_juegos == "5":
                    gestionar_versiones()
                elif opcion_juegos == "6":
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
                    input("Presione Enter para continuar...")
        
        elif opcion == "3":
            while True:
                mostrar_menu_eventos()
                opcion_eventos = input("Seleccione una opción: ")
                
                if opcion_eventos == "1":
                    listar_eventos()
                elif opcion_eventos == "2":
                    agregar_evento()
                elif opcion_eventos == "3":
                    editar_evento()
                elif opcion_eventos == "4":
                    print("Función no implementada aún")
                    input("Presione Enter para continuar...")
                elif opcion_eventos == "5":
                    gestionar_participantes()
                elif opcion_eventos == "6":
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
                    input("Presione Enter para continuar...")
        
        elif opcion == "4":
            while True:
                mostrar_menu_reportes()
                opcion_reportes = input("Seleccione una opción: ")
                
                if opcion_reportes == "1":
                    reporte_ventas()
                elif opcion_reportes == "2":
                    reporte_resenas()
                elif opcion_reportes == "3":
                    reporte_actividad_usuarios()
                elif opcion_reportes == "4":
                    exportar_datos_csv()
                elif opcion_reportes == "5":
                    break
                else:
                    print("Opción inválida. Intente nuevamente.")
                    input("Presione Enter para continuar...")
        
        elif opcion == "5":
            print("\n¡Gracias por usar el sistema!")
            break
        
        else:
            print("Opción inválida. Intente nuevamente.")
            input("Presione Enter para continuar...")

if __name__ == "__main__":
    main()