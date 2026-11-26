import { useState } from "react";
import Astar from "./components/astar/Astar";
import Fuzzy from "./components/fuzzy/Fuzzy";
import Cnn from "./components/cnn/Cnn";
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

          <button
            className={modulo === "cnn" ? "activo" : ""}
            onClick={() => setModulo("cnn")}
          >
            Diagnóstico de hojas
          </button>
        </nav>
      </header>
      <div hidden={modulo !== "cnn"}>
        <Cnn />
      </div>
      
      <div hidden={modulo !== "astar"}>
        <Astar />
      </div>

      <div hidden={modulo !== "fuzzy"}>
        <Fuzzy />
      </div>
    </div>
  );
}