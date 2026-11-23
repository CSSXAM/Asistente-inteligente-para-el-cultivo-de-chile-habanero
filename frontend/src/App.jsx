
import { useState } from "react";
import "./App.css";

const MAX_CELDAS = 2500;
const API_URL = "http://127.0.0.1:8000/api/astar/ruta";

const OBSTACULOS = [1, 2, 3];
const ESTILOS_PRIORIDAD = {
  alta: { fondo: "#dc2626", numero: "1", texto: "Alta" },
  media: { fondo: "#d97706", numero: "2", texto: "Media" },
  baja: { fondo: "#2563eb", numero: "3", texto: "Baja" },
};

const HERRAMIENTAS = [
  { id: "pasillo", nombre: "Pasillo", valor: 0 },
  { id: "hilera", nombre: "Hilera de plantas", valor: 1 },
  { id: "fijo", nombre: "Obstáculo fijo", valor: 2 },
  { id: "temporal", nombre: "Obstáculo temporal", valor: 3 },
  { id: "interes", nombre: "Punto de interés", valor: 4 },
  { id: "prioridad", nombre: "Asignar prioridad" },
  { id: "inicio", nombre: "Inicio" },
  { id: "destino", nombre: "Destino" },
];

function crearParcela(filas, columnas) {
  return Array.from(
    { length: filas },
    () => Array(columnas).fill(0)
  );
}

// Construye una trayectoria continua con carriles separados para ida y regreso.
// La separación es visual; las posiciones originales de A* no se modifican.
function construirTrayectoria(ruta) {
  if (ruta.length < 2) return { tramos: [], conexiones: [] };

  const claves = new Set();
  const clave = (a, b) => `${a[0]},${a[1]}>${b[0]},${b[1]}`;
  for (let i = 0; i < ruta.length - 1; i++) {
    claves.add(clave(ruta[i], ruta[i + 1]));
  }

  const centro = ([fila, columna]) => ({ x: columna * 54 + 25, y: fila * 54 + 25 });
  const tramos = ruta.slice(1).map((destino, i) => {
    const origen = ruta[i];
    const a = centro(origen);
    const b = centro(destino);
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const distancia = Math.hypot(dx, dy) || 1;
    // Desplazamiento a la derecha de la dirección del viaje.
    // En el sentido contrario se desplaza hacia el lado opuesto.
    const repetidoEnSentidoContrario = claves.has(clave(destino, origen));
    const desplazamiento = repetidoEnSentidoContrario ? 7 : 0;
    const ox = (-dy / distancia) * desplazamiento;
    const oy = (dx / distancia) * desplazamiento;
    return {
      inicio: { x: a.x + ox, y: a.y + oy },
      fin: { x: b.x + ox, y: b.y + oy },
      dx: dx / distancia,
      dy: dy / distancia,
    };
  });

  const conexiones = tramos.slice(1).map((tramo, i) => ({
    inicio: tramos[i].fin,
    fin: tramo.inicio,
  }));
  return { tramos, conexiones };
}

export default function App() {
  const [ancho, setAncho] = useState("30");
  const [largo, setLargo] = useState("30");
  const [tamanoCelda, setTamanoCelda] = useState("5");

  const [parcela, setParcela] = useState([]);
  const [herramienta, setHerramienta] = useState("hilera");
  const [prioridadActual, setPrioridadActual] = useState("alta");
  const [prioridades, setPrioridades] = useState({});
  const [modo, setModo] = useState("directa");
  const [visitados, setVisitados] = useState([]);

  const [inicio, setInicio] = useState(null);
  const [destino, setDestino] = useState(null);

  const [ruta, setRuta] = useState([]);
  const [costo, setCosto] = useState(null);
  const [movimientos, setMovimientos] = useState(null);

  const [error, setError] = useState("");
  const [mensaje, setMensaje] = useState("");
  const [calculando, setCalculando] = useState(false);

  const superficie =
    Number(ancho) * Number(largo) / 10000;

  function limpiarResultado() {
    setRuta([]);
    setVisitados([]);
    setCosto(null);
    setMovimientos(null);
    setMensaje("");
    setError("");
  }

  function generarParcela() {
    const anchoMetros = Number(ancho);
    const largoMetros = Number(largo);
    const escala = Number(tamanoCelda);

    if (
      !ancho.trim() ||
      !largo.trim() ||
      !tamanoCelda.trim() ||
      !Number.isFinite(anchoMetros) ||
      !Number.isFinite(largoMetros) ||
      !Number.isFinite(escala) ||
      anchoMetros <= 0 ||
      largoMetros <= 0 ||
      escala <= 0
    ) {
      setError("Ingresa dimensiones y escala válidas.");
      return;
    }

    const filas = Math.ceil(largoMetros / escala);
    const columnas = Math.ceil(anchoMetros / escala);

    if (filas * columnas > MAX_CELDAS) {
      setError(
        `La parcela supera ${MAX_CELDAS} celdas. ` +
        "Selecciona una escala mayor."
      );
      return;
    }

    setParcela(crearParcela(filas, columnas));
    setPrioridades({});
    setInicio(null);
    setDestino(null);
    limpiarResultado();
  }

  function modificarCelda(fila, columna) {
    if (calculando) return;

    const posicion = [fila, columna];
    const tipoActual = parcela[fila][columna];

    const clave = `${fila}-${columna}`;
    if (herramienta === "prioridad") {
      if (tipoActual !== 4) {
        setError("La prioridad solo se asigna a puntos de interés.");
        return;
      }
      setPrioridades((anterior) => ({...anterior, [clave]: prioridadActual}));
    } else if (herramienta === "inicio" || herramienta === "destino") {
      if (OBSTACULOS.includes(tipoActual)) {
        setError("No puedes seleccionar una celda no transitable.");
        return;
      }

      if (herramienta === "inicio") {
        setInicio(posicion);
      } else {
        setDestino(posicion);
      }
    } else {
      const valor = HERRAMIENTAS.find(
        (item) => item.id === herramienta
      ).valor;

      setPrioridades((anterior) => {
        const siguiente = {...anterior};
        // Los puntos nuevos quedan sin prioridad hasta que se les asigne.
        if (valor !== 4 || tipoActual !== 4) delete siguiente[clave];
        return siguiente;
      });
      setParcela((anterior) =>
        anterior.map((filaActual, indiceFila) =>
          filaActual.map((celda, indiceColumna) =>
            indiceFila === fila && indiceColumna === columna
              ? valor
              : celda
          )
        )
      );

      // Si una posición se convierte en obstáculo,
      // deja de ser válida como inicio o destino.
      if (OBSTACULOS.includes(valor)) {
        if (inicio?.[0] === fila && inicio?.[1] === columna) {
          setInicio(null);
        }

        if (destino?.[0] === fila && destino?.[1] === columna) {
          setDestino(null);
        }
      }
    }

    limpiarResultado();
  }

  async function calcularRuta() {
    if (!inicio || !destino) {
      setError("Selecciona un inicio y un destino.");
      return;
    }

    if (modo === "inspeccion") {
      const sinPrioridad = parcela.some((fila, f) =>
        fila.some((celda, c) => celda === 4 && !prioridades[`${f}-${c}`])
      );
      if (sinPrioridad) {
        setError("Asigna una prioridad a todos los puntos de interés antes de inspeccionar.");
        return;
      }
    }

    limpiarResultado();
    setCalculando(true);

    try {
      const respuesta = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          parcela,
          inicio,
          destino,
          modo,
          puntos: modo === "inspeccion" ? parcela.flatMap((fila, f) =>
            fila.flatMap((celda, c) => celda === 4 ? [{
              posicion: [f, c],
              prioridad: prioridades[`${f}-${c}`]
            }] : [])
          ) : [],
        }),
      });

      const datos = await respuesta.json();

      if (!respuesta.ok) {
        throw new Error(
          typeof datos.detail === "string"
            ? datos.detail
            : "No se pudo calcular la ruta."
        );
      }

      setRuta(datos.ruta ?? []);
      setVisitados(datos.puntos_visitados ?? []);
      setCosto(datos.costo);
      setMovimientos(datos.movimientos);
      setMensaje(datos.mensaje);
    } catch (err) {
      setError(err.message || "Error de conexión con FastAPI.");
    } finally {
      setCalculando(false);
    }
  }

  function esPosicion(posicion, fila, columna) {
    return posicion?.[0] === fila && posicion?.[1] === columna;
  }

  function estaEnRuta(fila, columna) {
    return ruta.some(
      ([f, c]) => f === fila && c === columna
    );
  }

  return (
    <main className="contenedor">
      <h1>Asistente IA para el cultivo de chile habanero</h1>
      <h2>Planificación de rutas con A*</h2>

      <section>
        <h3>Configuración del terreno</h3>

        <div className="herramientas">
          <label>
            Ancho (m)
            <input
              type="number"
              min="1"
              value={ancho}
              onChange={(e) => setAncho(e.target.value)}
            />
          </label>

          <label>
            Largo (m)
            <input
              type="number"
              min="1"
              value={largo}
              onChange={(e) => setLargo(e.target.value)}
            />
          </label>

          <label>
            Metros por celda
            <input
              type="number"
              min="0.1"
              step="0.1"
              value={tamanoCelda}
              onChange={(e) => setTamanoCelda(e.target.value)}
            />
          </label>
        </div>

        <p>
          Superficie estimada:{" "}
          <strong>
            {Number.isFinite(superficie) && superficie > 0
              ? superficie.toFixed(4)
              : "0"} ha
          </strong>
        </p>

        <button onClick={generarParcela} disabled={calculando}>
          Generar parcela
        </button>
      </section>

      {parcela.length > 0 && (
        <section>
          <h3>Editor de la parcela</h3>

          <p>
            Cuadrícula: {parcela.length} filas ×{" "}
            {parcela[0].length} columnas
          </p>

          <div className="herramientas">
            {HERRAMIENTAS.map((item) => (
              <button
                key={item.id}
                type="button"
                className={
                  herramienta === item.id ? "seleccionado" : ""
                }
                onClick={() => setHerramienta(item.id)}
              >
                {item.nombre}
              </button>
            ))}
          </div>

          {herramienta === "prioridad" && (
            <div>
              <label>Prioridad del punto:{" "}
                <select value={prioridadActual} onChange={(e) => setPrioridadActual(e.target.value)}>
                  <option value="alta">Alta (1 - rojo)</option>
                  <option value="media">Media (2 - naranja)</option>
                  <option value="baja">Baja (3 - azul)</option>
                </select>
              </label>
              <p>Selecciona una prioridad y haz clic en cada punto de interés para asignarla.</p>
              <label>Modo de ruta:{" "}
                <select value={modo} onChange={(e) => { setModo(e.target.value); limpiarResultado(); }}>
                  <option value="directa">Ruta directa</option>
                  <option value="inspeccion">Inspección de puntos de interés</option>
                </select>
              </label>
            </div>
          )}
          <p>Modo actual: <strong>{modo === "inspeccion" ? "Inspección de puntos de interés" : "Ruta directa"}</strong></p>

          <p>
            Herramienta seleccionada:{" "}
            <strong>{herramienta}</strong>
          </p>

          <div className="area-cuadricula">
            <div className="envoltura-cuadricula">
            <div
              className="cuadricula"
              style={{
                gridTemplateColumns:
                  `repeat(${parcela[0].length}, 50px)`,
                width: "max-content",
              }}
            >
              {parcela.map((fila, indiceFila) =>
                fila.map((celda, indiceColumna) => {
                  const esInicio = esPosicion(
                    inicio, indiceFila, indiceColumna
                  );

                  const esDestino = esPosicion(
                    destino, indiceFila, indiceColumna
                  );

                  const esRuta = estaEnRuta(
                    indiceFila, indiceColumna
                  );
                  const prioridadPunto = celda === 4
                    ? prioridades[`${indiceFila}-${indiceColumna}`]
                    : null;
                  const estiloPrioridad = prioridadPunto
                    ? ESTILOS_PRIORIDAD[prioridadPunto]
                    : null;

                  return (
                    <button
                      key={`${indiceFila}-${indiceColumna}`}
                      type="button"
                      className={[
                        "celda",
                        `tipo-${celda}`,
                        esRuta ? "en-ruta" : "",
                        esInicio ? "es-inicio" : "",
                        esDestino ? "es-destino" : "",
                      ].join(" ")}
                      onClick={() =>
                        modificarCelda(indiceFila, indiceColumna)
                      }
                      style={esRuta ? {
                        outline: "3px solid #22c55e",
                        outlineOffset: "-3px",
                      } : undefined}
                      title={`Fila ${indiceFila}, columna ${indiceColumna}${estiloPrioridad ? `, prioridad ${estiloPrioridad.texto}` : ""}`}
                      aria-label={`Celda ${indiceFila}, ${indiceColumna}${estiloPrioridad ? `, prioridad ${estiloPrioridad.texto}` : ""}`}
                    >
                      {esInicio ? "I" : esDestino ? "D" : estiloPrioridad ? (
                        <span
                          className="indicador-prioridad"
                          style={{ backgroundColor: estiloPrioridad.fondo }}
                          aria-hidden="true"
                        >
                          {estiloPrioridad.numero}
                        </span>
                      ) : esRuta ? "•" : ""}
                    </button>
                  );
                })
              )}
            </div>
            {ruta.length > 1 && (() => {
              const { tramos, conexiones } = construirTrayectoria(ruta);
              const linea = (a, b) => `M ${a.x} ${a.y} L ${b.x} ${b.y}`;
              const trayectoria = [
                ...tramos.map((t) => linea(t.inicio, t.fin)),
                ...conexiones.map((c) => linea(c.inicio, c.fin)),
              ].join(" ");
              return (
                <svg
                  className="flechas-recorrido"
                  width={parcela[0].length * 54 - 4}
                  height={parcela.length * 54 - 4}
                  viewBox={`0 0 ${parcela[0].length * 54 - 4} ${parcela.length * 54 - 4}`}
                  role="img"
                  aria-label="Ruta de inspección con flechas y carriles separados de ida y regreso"
                >
                  {/* Contorno oscuro para que la línea destaque sobre cualquier celda. */}
                  <path d={trayectoria} className="trayectoria-borde" />
                  <path d={trayectoria} className="trayectoria-linea" />
                  {tramos.map((tramo, i) => {
                    // Una flecha cada tres movimientos, también en el último.
                    if (i % 3 !== 1 && i !== tramos.length - 1) return null;
                    const x = tramo.inicio.x + (tramo.fin.x - tramo.inicio.x) * 0.62;
                    const y = tramo.inicio.y + (tramo.fin.y - tramo.inicio.y) * 0.62;
                    const ux = tramo.dx;
                    const uy = tramo.dy;
                    const largo = 11;
                    const ancho = 5.5;
                    const puntos = [
                      [x + ux * largo / 2, y + uy * largo / 2],
                      [x - ux * largo / 2 - uy * ancho, y - uy * largo / 2 + ux * ancho],
                      [x - ux * largo / 2 + uy * ancho, y - uy * largo / 2 - ux * ancho],
                    ].map(([px, py]) => `${px},${py}`).join(" ");
                    return <polygon key={i} points={puntos} className="trayectoria-flecha" />;
                  })}
                </svg>
              );
            })()}
            </div>
          </div>

          <button
            onClick={calcularRuta}
            disabled={calculando || !inicio || !destino}
          >
            {calculando ? "Calculando..." : "Calcular ruta"}
          </button>

          {mensaje && <p>{mensaje}</p>}
          {modo === "inspeccion" && mensaje && <p>Puntos inspeccionados: {visitados.length}</p>}

          {costo !== null && (
            <p>
              Costo: <strong>{costo}</strong> |{" "}
              Movimientos: <strong>{movimientos}</strong>
            </p>
          )}
        </section>
      )}

      {error && <p role="alert" className="error">{error}</p>}
    </main>
  );
}
