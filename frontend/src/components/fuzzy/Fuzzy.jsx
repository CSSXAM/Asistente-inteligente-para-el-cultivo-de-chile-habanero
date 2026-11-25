import { useState } from "react";
import "./Fuzzy.css";

const API_URL = "http://127.0.0.1:8000/api/fuzzy/riego";

const ETAPAS = [
  { id: 1, nombre: "Vivero" },
  { id: 2, nombre: "Trasplante" },
  { id: 3, nombre: "Vegetativo" },
  { id: 4, nombre: "Floración" },
  { id: 5, nombre: "Fructificación" },
  { id: 6, nombre: "Cosecha" },
];

export default function Fuzzy() {
  const [humedad, setHumedad] = useState(40);
  const [temperatura, setTemperatura] = useState(34);
  const [etapa, setEtapa] = useState(5);

  const [resultado, setResultado] = useState(null);
  const [calculando, setCalculando] = useState(false);
  const [error, setError] = useState("");

  const minutos = resultado?.minutos_riego ?? 0;
  const porcentaje = (minutos / 60) * 100;

  async function calcularRiego(event) {
    event.preventDefault();

    setError("");
    setResultado(null);

    if (
      humedad === "" ||
      !Number.isFinite(Number(humedad)) ||
      Number(humedad) < 0 ||
      Number(humedad) > 100
    ) {
      setError("La humedad debe estar entre 0 y 100 %.");
      return;
    }

    if (
      temperatura === "" ||
      !Number.isFinite(Number(temperatura)) ||
      Number(temperatura) < 0 ||
      Number(temperatura) > 50
    ) {
      setError("La temperatura debe estar entre 0 y 50 °C.");
      return;
    }

    setCalculando(true);

    try {
      const respuesta = await fetch(API_URL, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          humedad: Number(humedad),
          temperatura: Number(temperatura),
          etapa: Number(etapa),
        }),
      });

      const datos = await respuesta.json();

      if (!respuesta.ok) {
        throw new Error(
          typeof datos.detail === "string"
            ? datos.detail
            : "No fue posible calcular la recomendación."
        );
      }

      setResultado(datos);
    } catch (err) {
      setError(err.message);
    } finally {
      setCalculando(false);
    }
  }

  return (
    <section className="fuzzy-module">
      <header className="fuzzy-header">
        <h2>Controlador difuso de riego</h2>
        <p>Simulación de las condiciones del cultivo</p>
      </header>

      <div className="fuzzy-grid">

        {/* Panel de configuración */}

        <form
          className="fuzzy-panel"
          onSubmit={calcularRiego}
        >
          <h3>Configuración del cultivo</h3>

          <div className="fuzzy-field">
            <label htmlFor="fuzzy-humedad">
              Humedad aprovechable del suelo (%)
            </label>

            <input
              id="fuzzy-humedad"
              type="number"
              min="0"
              max="100"
              step="0.1"
              value={humedad}
              onChange={(e) => setHumedad(e.target.value)}
              required
            />

            <input
              type="range"
              min="0"
              max="100"
              step="0.1"
              aria-label="Ajustar humedad"
              value={humedad === "" ? 0 : humedad}
              onChange={(e) =>
                setHumedad(Number(e.target.value))
              }
            />

            <div className="fuzzy-range-labels">
              <span>0%</span>
              <span>100%</span>
            </div>

            <small>
              Porcentaje de agua aprovechable restante.
            </small>
          </div>

          <div className="fuzzy-field">
            <label htmlFor="fuzzy-temperatura">
              Temperatura ambiental (°C)
            </label>

            <input
              id="fuzzy-temperatura"
              type="number"
              min="0"
              max="50"
              step="0.1"
              value={temperatura}
              onChange={(e) =>
                setTemperatura(e.target.value)
              }
              required
            />

            <input
              type="range"
              min="0"
              max="50"
              step="0.1"
              aria-label="Ajustar temperatura"
              value={temperatura === "" ? 0 : temperatura}
              onChange={(e) =>
                setTemperatura(Number(e.target.value))
              }
            />

            <div className="fuzzy-range-labels">
              <span>0 °C</span>
              <span>50 °C</span>
            </div>
          </div>

          <div className="fuzzy-field">
            <label htmlFor="fuzzy-etapa">
              Etapa fenológica
            </label>

            <select
              id="fuzzy-etapa"
              value={etapa}
              onChange={(e) =>
                setEtapa(Number(e.target.value))
              }
            >
              {ETAPAS.map((item) => (
                <option key={item.id} value={item.id}>
                  {item.nombre}
                </option>
              ))}
            </select>
          </div>

          <button
            className="fuzzy-button"
            type="submit"
            disabled={calculando}
          >
            {calculando
              ? "Calculando..."
              : "Calcular recomendación"}
          </button>

          {error && (
            <p className="fuzzy-error" role="alert">
              {error}
            </p>
          )}
        </form>

        {/* Panel de resultados */}

        <div className="fuzzy-panel" aria-live="polite">
          <h3>Recomendación de riego</h3>

          <div className="fuzzy-gauge">
            <svg viewBox="0 0 220 140">

              <path
                className="fuzzy-gauge-background"
                d="M 20 110 A 90 90 0 0 1 200 110"
                pathLength="100"
              />

              <path
                className="fuzzy-gauge-progress"
                d="M 20 110 A 90 90 0 0 1 200 110"
                pathLength="100"
                strokeDasharray={`${porcentaje} 100`}
                opacity={minutos > 0 ? 1 : 0}
              />

              <text
                x="110"
                y="85"
                className="fuzzy-gauge-value"
              >
                {resultado ? minutos.toFixed(2) : "--"}
              </text>

              <text
                x="110"
                y="105"
                className="fuzzy-gauge-unit"
              >
                minutos
              </text>

              <text x="20" y="135" className="fuzzy-gauge-unit">
                0
              </text>

              <text x="200" y="135" className="fuzzy-gauge-unit">
                60
              </text>
            </svg>
          </div>

          <p className="fuzzy-result-status">
            {!resultado
              ? "Esperando condiciones del cultivo"
              : minutos === 0
                ? "No se requiere riego"
                : "Riego recomendado"}
          </p>

          <div className="fuzzy-result-details">

            <div className="fuzzy-result-item">
              <span>Agua estimada por gotero</span>
              <strong>
                {resultado
                  ? `${resultado.litros_estimados_por_gotero.toFixed(3)} L`
                  : "--"}
              </strong>
            </div>

            <div className="fuzzy-result-item">
              <span>Caudal de referencia</span>
              <strong>
                {resultado
                  ? `${resultado.caudal_litros_hora} L/h`
                  : "--"}
              </strong>
            </div>

            <div className="fuzzy-result-item">
              <span>Etapa evaluada</span>
              <strong>
                {resultado
                  ? resultado.etapa
                  : "--"}
              </strong>
            </div>

          </div>
        </div>
      </div>

      {/* Historial pendiente de integración */}

      <div className="fuzzy-panel fuzzy-history">
        <h3>Historial de recomendaciones</h3>

        <div className="fuzzy-table-container">
          <table>
            <thead>
              <tr>
                <th>Fecha</th>
                <th>Humedad</th>
                <th>Temperatura</th>
                <th>Etapa</th>
                <th>Tiempo de riego</th>
                <th>Agua por gotero</th>
              </tr>
            </thead>

            <tbody>
              <tr>
                <td colSpan="6" className="fuzzy-empty">
                  Historial pendiente de integración con MySQL.
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </section>
  );
}