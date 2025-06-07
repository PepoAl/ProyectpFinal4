create database gaming_platform1

CREATE TABLE Usuario (
    id_usuario SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contraseña TEXT NOT NULL,
    rol_usuario VARCHAR(20) NOT NULL, -- tipo personalizado
    fecha_registro DATE NOT NULL DEFAULT CURRENT_DATE
);
CREATE TABLE PerfilUsuario (
    id_perfil SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario) ON DELETE CASCADE,
    avatar_url TEXT,
    pais VARCHAR(50),
    biografia TEXT,
    fecha_nacimiento DATE
);
CREATE TABLE Juego (
    id_juego SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    fecha_lanzamiento DATE,
    precio NUMERIC(10,2) NOT NULL,
    estado_juego VARCHAR(20) NOT NULL, -- tipo personalizado
    id_desarrollador INTEGER REFERENCES Usuario(id_usuario)
);
CREATE TABLE VersionJuego (
    id_version SERIAL PRIMARY KEY,
    id_juego INTEGER REFERENCES Juego(id_juego) ON DELETE CASCADE,
    numero_version VARCHAR(20),
    fecha_publicacion DATE,
    notas_cambios TEXT
);
CREATE TABLE Compra (
    id_compra SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_juego INTEGER REFERENCES Juego(id_juego),
    fecha_compra TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    monto_pagado NUMERIC(10,2),
    metodo_pago VARCHAR(20) -- tipo personalizado
);

CREATE TABLE Reseña (
    id_reseña SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_juego INTEGER REFERENCES Juego(id_juego),
    calificacion INTEGER CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha_reseña DATE
);
CREATE TABLE Logro (
    id_logro SERIAL PRIMARY KEY,
    id_juego INTEGER REFERENCES Juego(id_juego) ON DELETE CASCADE,
    nombre VARCHAR(100),
    descripcion TEXT,
    puntos INTEGER
);
CREATE TABLE ProgresoUsuarioLogro (
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_logro INTEGER REFERENCES Logro(id_logro),
    fecha_desbloqueo DATE,
    PRIMARY KEY (id_usuario, id_logro)
);
CREATE TABLE Categoria (
    id_categoria SERIAL PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL
);
CREATE TABLE JuegoCategoria (
    id_juego INTEGER REFERENCES Juego(id_juego),
    id_categoria INTEGER REFERENCES Categoria(id_categoria),
    PRIMARY KEY (id_juego, id_categoria)
);
CREATE TABLE JuegoPlataforma (
    id_juego INTEGER REFERENCES Juego(id_juego),
    plataforma VARCHAR(20), -- tipo personalizado
    PRIMARY KEY (id_juego, plataforma)
);
CREATE TABLE JuegoFavorito (
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_juego INTEGER REFERENCES Juego(id_juego),
    fecha_marcado DATE,
    PRIMARY KEY (id_usuario, id_juego)
);
CREATE TABLE Evento (
    id_evento SERIAL PRIMARY KEY,
    titulo VARCHAR(100),
    descripcion TEXT,
    fecha_inicio DATE,
    fecha_fin DATE,
    tipo_evento VARCHAR(20) -- tipo personalizado
);
CREATE TABLE ParticipacionEvento (
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    id_evento INTEGER REFERENCES Evento(id_evento),
    fecha_inscripcion DATE,
    PRIMARY KEY (id_usuario, id_evento)
);
CREATE TABLE Comentario (
    id_comentario SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    tipo_objetivo VARCHAR(20), -- Juego o Evento
    id_objetivo INTEGER, -- puede ser id_juego o id_evento según el tipo
    contenido TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE ReporteComentario (
    id_reporte SERIAL PRIMARY KEY,
    id_comentario INTEGER REFERENCES Comentario(id_comentario),
    motivo TEXT,
    fecha_reporte DATE DEFAULT CURRENT_DATE
);


CREATE TABLE BitacoraActividad (
    id_actividad SERIAL PRIMARY KEY,
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    tipo_actividad VARCHAR(50), -- ej. 'Compra', 'Reseña', 'Logro'
    descripcion TEXT,
    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE MantenimientoJuego (
    id_mantenimiento SERIAL PRIMARY KEY,
    id_juego INTEGER REFERENCES Juego(id_juego),
    fecha_inicio TIMESTAMP,
    fecha_fin TIMESTAMP,
    motivo TEXT
);
CREATE TABLE HistorialPrecio (
    id_historial SERIAL PRIMARY KEY,
    id_juego INTEGER REFERENCES Juego(id_juego),
    precio_anterior NUMERIC(10,2),
    precio_nuevo NUMERIC(10,2),
    fecha_cambio DATE
);
CREATE TABLE ReporteJuego (
    id_reporte SERIAL PRIMARY KEY,
    id_juego INTEGER REFERENCES Juego(id_juego),
    id_usuario INTEGER REFERENCES Usuario(id_usuario),
    motivo TEXT,
    fecha_reporte DATE DEFAULT CURRENT_DATE
);


CREATE TYPE rol_usuario AS ENUM ('Jugador', 'Desarrollador');
CREATE TYPE estado_juego AS ENUM ('Beta', 'Lanzado', 'Retirado');
CREATE TYPE metodo_pago AS ENUM ('Tarjeta', 'Paypal', 'Crédito', 'Cripto');
CREATE TYPE tipo_evento AS ENUM ('Lanzamiento', 'Torneo', 'Rebaja');
CREATE TYPE tipo_objetivo AS ENUM ('Juego', 'Evento');
CREATE TYPE plataforma AS ENUM ('Windows', 'Linux', 'Mac', 'Android', 'iOS');


---Funciones 
---Calcular promedio de calificación de un juego
CREATE OR REPLACE FUNCTION obtener_promedio_juego(juego_id INT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (
    SELECT AVG(calificacion)::NUMERIC(3,2)
    FROM Reseña
    WHERE id_juego = juego_id
  );
END;
$$ LANGUAGE plpgsql;

---Total gastado por usuario
CREATE OR REPLACE FUNCTION total_gastado_usuario(usuario_id INT)
RETURNS NUMERIC AS $$
BEGIN
  RETURN (
    SELECT SUM(monto_pagado)
    FROM Compra
    WHERE id_usuario = usuario_id
  );
END;
$$ LANGUAGE plpgsql;

---Número de logros desbloqueados por usuario
CREATE OR REPLACE FUNCTION contar_logros_usuario(usuario_id INT)
RETURNS INTEGER AS $$
BEGIN
  RETURN (
    SELECT COUNT(*) FROM ProgresoUsuarioLogro
    WHERE id_usuario = usuario_id
  );
END;
$$ LANGUAGE plpgsql;

---Triggers 
---Insertar automáticamente en BitacoraActividad cuando se hace una compra
CREATE OR REPLACE FUNCTION registrar_compra()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO BitacoraActividad(id_usuario, tipo_actividad, descripcion)
  VALUES (
    NEW.id_usuario,
    'Compra',
    'Compra del juego ID ' || NEW.id_juego
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_registrar_compra
AFTER INSERT ON Compra
FOR EACH ROW
EXECUTE FUNCTION registrar_compra();

---Insertar en HistorialPrecio cuando se actualiza el precio de un juego
CREATE OR REPLACE FUNCTION guardar_historial_precio()
RETURNS TRIGGER AS $$
BEGIN
  IF OLD.precio IS DISTINCT FROM NEW.precio THEN
    INSERT INTO HistorialPrecio(id_juego, precio_anterior, precio_nuevo, fecha_cambio)
    VALUES (OLD.id_juego, OLD.precio, NEW.precio, CURRENT_DATE);
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_precio_juego
BEFORE UPDATE ON Juego
FOR EACH ROW
EXECUTE FUNCTION guardar_historial_precio();

--- Insertar actividad cuando se desbloquea un logro
CREATE OR REPLACE FUNCTION registrar_logro()
RETURNS TRIGGER AS $$
DECLARE
  nombre_logro TEXT;
BEGIN
  SELECT nombre INTO nombre_logro FROM Logro WHERE id_logro = NEW.id_logro;
  INSERT INTO BitacoraActividad(id_usuario, tipo_actividad, descripcion)
  VALUES (
    NEW.id_usuario,
    'Logro',
    'Desbloqueó: ' || nombre_logro
  );
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_logro
AFTER INSERT ON ProgresoUsuarioLogro
FOR EACH ROW
EXECUTE FUNCTION registrar_logro();


UPDATE usuario
SET rol_usuario = 'JUGADOR'
WHERE rol_usuario = 'Jugador';

UPDATE usuario
SET rol_usuario = 'DESARROLLADOR'
WHERE rol_usuario = 'Desarrollador';

UPDATE juego
SET estado_juego = 'BETA'
WHERE estado_juego = 'Beta';

UPDATE juego
SET estado_juego = 'LANZADO'
WHERE estado_juego = 'Lanzado';

UPDATE juego
SET estado_juego = 'RETIRADO'
WHERE estado_juego = 'Retirado';

UPDATE compra
SET metodo_pago = 'TARJETA'
WHERE metodo_pago = 'Tarjeta';

UPDATE compra
SET metodo_pago = 'PAYPAL'
WHERE metodo_pago = 'Paypal';

UPDATE compra
SET metodo_pago = 'CREDITO'
WHERE metodo_pago = 'Crédito';

UPDATE compra
SET metodo_pago = 'CRIPTO'
WHERE metodo_pago = 'Cripto';