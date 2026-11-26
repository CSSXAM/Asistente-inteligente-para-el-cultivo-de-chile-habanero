
import { useState, useEffect, useRef } from "react";
import "./Cnn.css";

const BASE_URL = "http://127.0.0.1:8000";

const API_URL = `${BASE_URL}/api/cnn/clasificar`;
const HISTORIAL_URL = `${BASE_URL}/api/cnn/historial`;

const MAX_ARCHIVO = 10 * 1024 * 1024;

const FORMATOS = [
  "image/jpeg",
  "image/png",
  "image/webp",
];

const ADVERTENCIA =
  "Resultado experimental. El modelo fue entrenado con imágenes de pimiento y no está validado para el diagnóstico fitosanitario del chile habanero.";

function formatearFecha(fecha) {
  if (!fecha) return "";

  const [dia, hora] = fecha.replace(" ", "T").split("T");

  return `${dia.split("-").reverse().join("/")} ${hora ?? ""}`;
}

export default function Cnn() {

  // Estados del análisis

  const [imagen, setImagen] = useState(null);
  const [vistaPrevia, setVistaPrevia] = useState("");
  const [resultado, setResultado] = useState(null);
  const [analizando, setAnalizando] = useState(false);
  const [error, setError] = useState("");

  // Estados del historial

  const [historial, setHistorial] = useState([]);
  const [cargandoHistorial, setCargandoHistorial] = useState(true);
  const [errorHistorial, setErrorHistorial] = useState("");
  const [revisionHistorial, setRevisionHistorial] = useState(0);

  // Recuperación de análisis anteriores

  const [registroSeleccionado, setRegistroSeleccionado] = useState(null);
  const [errorImagenHistorica, setErrorImagenHistorica] = useState(false);

  const inputImagen = useRef(null);
  const inicioModulo = useRef(null);

  // Generar y liberar la vista previa

 useEffect(() => {
  return () => {
    if (vistaPrevia) {
      URL.revokeObjectURL(vistaPrevia);
    }
  };
}, [vistaPrevia]);

  // Actualizar historial

  function actualizarHistorial() {

    setCargandoHistorial(true);
    setErrorHistorial("");

    setRevisionHistorial((revision) => revision + 1);

  }

  // Consultar historial desde FastAPI

  useEffect(() => {

    const control = new AbortController();

    fetch(HISTORIAL_URL, {
      signal: control.signal,
    })

      .then((respuesta) => {

        if (!respuesta.ok) {
          throw new Error(
            "No fue posible consultar el historial."
          );
        }

        return respuesta.json();

      })

      .then((datos) => {

        if (!Array.isArray(datos)) {
          throw new Error(
            "El historial recibido no es válido."
          );
        }

        if (!control.signal.aborted) {
          setHistorial(datos);
        }

      })

      .catch((err) => {

        if (!control.signal.aborted) {

          setErrorHistorial(
            err instanceof TypeError
              ? "No fue posible conectar con el servidor."
              : err.message
          );

        }

      })

      .finally(() => {

        if (!control.signal.aborted) {
          setCargandoHistorial(false);
        }

      });

    return () => control.abort();

  }, [revisionHistorial]);

  // Recuperar un análisis histórico

  function verAnalisis(registro) {

    if (analizando) return;

    setImagen(null);
    setVistaPrevia("");
    setError("");
    setErrorImagenHistorica(false);

    setRegistroSeleccionado(registro);

    setResultado({
      ...registro,
      advertencia: ADVERTENCIA,
    });

    if (inputImagen.current) {
      inputImagen.current.value = "";
    }

    inicioModulo.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

  }

  // Iniciar un nuevo análisis

  function nuevoAnalisis() {

    if (analizando) return;

    setRegistroSeleccionado(null);
    setImagen(null);
    setVistaPrevia("");
    setResultado(null);
    setError("");
    setErrorImagenHistorica(false);

    if (inputImagen.current) {
      inputImagen.current.value = "";
    }

    inicioModulo.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });

  }

  // Seleccionar fotografía

  function seleccionarImagen(event) {

    const archivo = event.target.files?.[0];

    setError("");
    setResultado(null);
    setImagen(null);
    setVistaPrevia("");
    setRegistroSeleccionado(null);
    setErrorImagenHistorica(false);

    if (!archivo) return;

    if (!FORMATOS.includes(archivo.type)) {

      setError("Selecciona una imagen JPG, PNG o WEBP.");
      event.target.value = "";
      return;

    }

    if (archivo.size === 0) {

      setError("La imagen está vacía.");
      event.target.value = "";
      return;

    }

    if (archivo.size > MAX_ARCHIVO) {

      setError("La imagen supera el límite de 10 MB.");
      event.target.value = "";
      return;

    }

    setImagen(archivo);
    setVistaPrevia(URL.createObjectURL(archivo));

  }

  // Enviar fotografía al backend

  async function analizarImagen(event) {

    event.preventDefault();

    if (analizando || registroSeleccionado) return;

    setError("");
    setResultado(null);

    if (!imagen) {

      setError("Selecciona una fotografía.");
      return;

    }

    setAnalizando(true);

    try {

      const formulario = new FormData();

      formulario.append("imagen", imagen);

      const respuesta = await fetch(API_URL, {
        method: "POST",
        body: formulario,
      });

      const datos = await respuesta.json();

      if (!respuesta.ok) {

        throw new Error(
          typeof datos.detail === "string"
            ? datos.detail
            : "No fue posible analizar la fotografía."
        );

      }

      setResultado(datos);

      actualizarHistorial();

    } catch (err) {

      setError(
        err instanceof TypeError
          ? "No fue posible conectar con el servidor."
          : err.message
      );

    } finally {

      setAnalizando(false);

    }

  }

  return (

    <section className="cnn-module">

      {/* Encabezado */}

      <header
        className="cnn-header"
        id="cnn-inicio"
        ref={inicioModulo}
      >

        <h2>Diagnóstico neuronal de hojas</h2>

        <p>
          Clasificación experimental mediante MobileNetV2
        </p>

        <div className="cnn-toolbar">

          <span className="cnn-modo">

            {registroSeleccionado
              ? `Consultando análisis #${registroSeleccionado.id}`
              : "Nuevo análisis"}

          </span>

          <button
            type="button"
            className="cnn-nuevo"
            onClick={nuevoAnalisis}
            disabled={analizando}
          >
            + Nuevo análisis
          </button>

        </div>

      </header>

      <div className="cnn-grid">

        {/* Panel de fotografías */}

        <form
          className="cnn-panel"
          onSubmit={analizarImagen}
        >

          <h3>Fotografía de la hoja</h3>

          <div className="cnn-preview">

            {registroSeleccionado ? (

              errorImagenHistorica ? (

                <div className="cnn-placeholder">

                  <span>Fotografía no disponible</span>

                  <small>
                    No fue posible recuperar el archivo original.
                  </small>

                </div>

              ) : (

                <img
                  key={registroSeleccionado.id}
                  src={`${BASE_URL}/${registroSeleccionado.ruta_imagen}`}
                  alt="Fotografía del análisis histórico"
                  onError={() => setErrorImagenHistorica(true)}
                />

              )

            ) : imagen && vistaPrevia ? (

              <img
                src={vistaPrevia}
                alt="Fotografía seleccionada para analizar"
              />

            ) : (

              <div className="cnn-placeholder">

                <span>Sin fotografía seleccionada</span>

                <small>
                  Selecciona una imagen de una hoja.
                </small>

              </div>

            )}

          </div>

          {/* Información histórica o carga de imágenes */}

          {registroSeleccionado ? (

            <div className="cnn-info-historica">

              <strong>Información del registro</strong>

              <p>
                <b>ID:</b> {registroSeleccionado.id}
              </p>

              <p>
                <b>Fecha:</b>{" "}
                {formatearFecha(
                  registroSeleccionado.fecha_registro
                )}
              </p>

              <p>
                <b>Archivo:</b>{" "}
                {registroSeleccionado.nombre_imagen}
              </p>

              <small>
                Estás consultando un análisis almacenado.
                No se ejecutará nuevamente la CNN.
              </small>

            </div>

          ) : (

            <>

              <div className="cnn-field">

                <label htmlFor="cnn-imagen">
                  Seleccionar fotografía
                </label>

                <input
                  ref={inputImagen}
                  id="cnn-imagen"
                  type="file"
                  accept="image/jpeg,image/png,image/webp"
                  onChange={seleccionarImagen}
                  disabled={analizando}
                />

                <small>
                  JPG, PNG o WEBP. Máximo 10 MB.
                </small>

              </div>

              <button
                className="cnn-button"
                type="submit"
                disabled={analizando || !imagen}
              >

                {analizando
                  ? "Analizando fotografía..."
                  : "Analizar imagen"}

              </button>

            </>

          )}

          {error && (

            <p className="cnn-error" role="alert">
              {error}
            </p>

          )}

        </form>

        {/* Panel de resultados */}

        <div
          className="cnn-panel"
          aria-live="polite"
        >

          <h3>Resultado del análisis</h3>

          {resultado ? (

            <>

              <div
                className={`cnn-diagnostico ${resultado.clase}`}
              >

                <span>
                  {resultado.diagnostico}
                </span>

                <strong>
                  {Number(resultado.confianza).toFixed(2)}%
                </strong>

                <small>
                  Confianza del modelo
                </small>

              </div>

              {/* Probabilidades */}

              <div className="cnn-probabilidades">

                <div className="cnn-probabilidad">

                  <div className="cnn-probabilidad-label">

                    <span>Sana</span>

                    <strong>
                      {Number(
                        resultado.probabilidad_sana
                      ).toFixed(2)}%
                    </strong>

                  </div>

                  <div className="cnn-barra">

                    <div
                      className="cnn-barra-sana"
                      style={{
                        width: `${resultado.probabilidad_sana}%`,
                      }}
                    />

                  </div>

                </div>

                <div className="cnn-probabilidad">

                  <div className="cnn-probabilidad-label">

                    <span>Enferma</span>

                    <strong>
                      {Number(
                        resultado.probabilidad_enferma
                      ).toFixed(2)}%
                    </strong>

                  </div>

                  <div className="cnn-barra">

                    <div
                      className="cnn-barra-enferma"
                      style={{
                        width: `${resultado.probabilidad_enferma}%`,
                      }}
                    />

                  </div>

                </div>

              </div>

              {/* Recomendación */}

              <div className="cnn-recomendacion">

                <h4>Recomendación</h4>

                <p>
                  {resultado.recomendacion}
                </p>

              </div>

            </>

          ) : (

            <div className="cnn-resultado-vacio">

              {analizando
                ? "Procesando la fotografía mediante la CNN..."
                : "Esperando una fotografía para analizar."}

            </div>

          )}

        </div>

      </div>

      {/* Limitaciones del modelo */}

      <div className="cnn-advertencia">

        <strong>
          Limitaciones del modelo
        </strong>

        <p>
          {resultado?.advertencia ?? ADVERTENCIA}
        </p>

        <small>
          La confianza representa una puntuación del modelo,
          no una certeza fitosanitaria.
        </small>

      </div>

      {/* Historial de clasificaciones */}

      <div className="cnn-panel cnn-history">

        <div className="cnn-history-header">

          <h3>Historial de clasificaciones</h3>

          <button
            type="button"
            className="cnn-retry"
            onClick={actualizarHistorial}
            disabled={cargandoHistorial}
          >
            Actualizar historial
          </button>

        </div>

        <div className="cnn-table-container">

          <table>

            <thead>

              <tr>
                <th>Fecha</th>
                <th>Fotografía</th>
                <th>Diagnóstico</th>
                <th>Confianza</th>
                <th>Recomendación</th>
                <th>Acciones</th>
              </tr>

            </thead>

            <tbody>

              {cargandoHistorial ? (

                <tr>

                  <td colSpan="6" className="cnn-empty">
                    Cargando historial...
                  </td>

                </tr>

              ) : errorHistorial ? (

                <tr>

                  <td colSpan="6" className="cnn-empty">

                    <p className="cnn-error" role="alert">
                      {errorHistorial}
                    </p>

                    <button
                      type="button"
                      className="cnn-retry"
                      onClick={actualizarHistorial}
                    >
                      Reintentar
                    </button>

                  </td>

                </tr>

              ) : historial.length === 0 ? (

                <tr>

                  <td colSpan="6" className="cnn-empty">
                    No hay clasificaciones registradas.
                  </td>

                </tr>

              ) : (

                historial.map((registro) => (

                  <tr
                    key={registro.id}
                    className={
                      registroSeleccionado?.id === registro.id
                        ? "cnn-fila-activa"
                        : ""
                    }
                  >

                    <td>
                      {formatearFecha(
                        registro.fecha_registro
                      )}
                    </td>

                    <td className="cnn-nombre-imagen">
                      {registro.nombre_imagen}
                    </td>

                    <td>

                      <span
                        className={`cnn-etiqueta ${registro.clase}`}
                      >
                        {registro.diagnostico}
                      </span>

                    </td>

                    <td>
                      {Number(
                        registro.confianza
                      ).toFixed(2)}%
                    </td>

                    <td>
                      {registro.recomendacion}
                    </td>

                    <td>

                      <button
                        type="button"
                        className={`cnn-ver ${
                          registroSeleccionado?.id === registro.id
                            ? "seleccionado"
                            : ""
                        }`}
                        onClick={() => verAnalisis(registro)}
                        disabled={analizando}
                        aria-pressed={
                          registroSeleccionado?.id === registro.id
                        }
                      >

                        {registroSeleccionado?.id === registro.id
                          ? "Abierto"
                          : "Ver análisis"}

                      </button>

                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

      </div>

    </section>

  );

}
