import { useState } from "react";
import Astar from "./components/astar/Astar";
import "./App.css";

export default function App() {
  const [modulo, setModulo] = useState("astar");

  return (
    <div className="aplicacion">
      <header className="encabezado">
        <h1>Asistente inteligente para el cultivo de chile habanero</h1>

        <nav className="navegacion">
          <button
            className={modulo === "astar" ? "activo" : ""}
            onClick={() => setModulo("astar")}
          >
            Planificación de rutas
          </button>

          <button
            className={modulo === "fuzzy" ? "activo" : ""}
            onClick={() => setModulo("fuzzy")}
          >
            Controlador de riego
          </button>

          <button disabled>
            Diagnóstico de hojas
          </button>
        </nav>
      </header>

      <div hidden={modulo !== "astar"}>
        <Astar />
      </div>

      <div hidden={modulo !== "fuzzy"}>
        <h2>Controlador difuso de riego</h2>
        <p>Módulo en desarrollo.</p>
      </div>
    </div>
  );
}