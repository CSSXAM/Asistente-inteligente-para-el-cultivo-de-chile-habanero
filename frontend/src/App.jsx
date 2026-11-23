
import { useState } from "react";
import "./App.css";

const MAX_CELDAS = 2500;
const API_URL = "http://127.0.0.1:8000/api/astar/ruta";

const OBSTACULOS = [1, 2, 3];

const HERRAMIENTAS = [
  { id: "pasillo", nombre: "Pasillo", valor: 0 },
  { id: "hilera", nombre: "Hilera de plantas", valor: 1 },
  { id: "fijo", nombre: "Obstáculo fijo", valor: 2 },
  { id: "temporal", nombre: "Obstáculo temporal", valor: 3 },
  { id: "interes", nombre: "Punto de interés", valor: 4 },
  { id: "inicio", nombre: "Inicio" },
  { id: "destino", nombre: "Destino" },
];

function crearParcela(filas, columnas) {
  return Array.from(
    { length: filas },
    () => Array(columnas).fill(0)
  );
}

export default function App() {
  const [ancho, setAncho] = useState("30");
  const [largo, setLargo] = useState("30");
  const [tamanoCelda, setTamanoCelda] = useState("5");

  const [parcela, setParcela] = useState([]);
  const [herramienta, setHerramienta] = useState("hilera");

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
    setInicio(null);
    setDestino(null);
    limpiarResultado();
  }

  function modificarCelda(fila, columna) {
    if (calculando) return;

    const posicion = [fila, columna];
    const tipoActual = parcela[fila][columna];

    if (herramienta === "inicio" || herramienta === "destino") {
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

          <p>
            Herramienta seleccionada:{" "}
            <strong>{herramienta}</strong>
          </p>

          <div className="area-cuadricula">
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
                      title={`Fila ${indiceFila}, columna ${indiceColumna}`}
                      aria-label={`Celda ${indiceFila}, ${indiceColumna}`}
                    >
                      {esInicio ? "I" : esDestino ? "D" : esRuta ? "•" : ""}
                    </button>
                  );
                })
              )}
            </div>
          </div>

          <button
            onClick={calcularRuta}
            disabled={calculando || !inicio || !destino}
          >
            {calculando ? "Calculando..." : "Calcular ruta"}
          </button>

          {mensaje && <p>{mensaje}</p>}

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
