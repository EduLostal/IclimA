import { useState } from "react";
import logo from './assets/logoIclimA.png';

function App() {
  const [estacion, setEstacion] = useState("3195");
  const [fecha, setFecha] = useState("");
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  // Obtener la fecha máxima permitida (hoy +1) 
  const getMaxFecha = () => {
    const ahora = new Date();
    ahora.setUTCHours(ahora.getUTCHours() + 1); 
    ahora.setDate(ahora.getDate() + 1);

    const año = ahora.getFullYear();
    const mes = String(ahora.getMonth() + 1).padStart(2, "0");
    const dia = String(ahora.getDate()).padStart(2, "0");

    return `${año}-${mes}-${dia}`;
  };

  const handlePredict = async () => {
    if (!fecha) return;

    setCargando(true);
    setResultado(null);
    setError(null);

    try {
      const response = await fetch("http://127.0.0.1:8000/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ fecha, estacion }),
      });

      if (!response.ok) throw new Error("No se pudo predecir esa fecha");

      const data = await response.json();
      setResultado(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  const handleConsultar = async () => {
    if (!fecha) return;

    setCargando(true);
    setResultado(null);
    setError(null);

    try {
      const response = await fetch(`http://127.0.0.1:8000/historico?fecha=${fecha}&estacion=${estacion}`);
      if (!response.ok) throw new Error("No se encontró información histórica para esa fecha");

      const data = await response.json();
      setResultado(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="container">
      <img src={logo} alt="Logo IclimA" className="logo" />

      <form onSubmit={(e) => e.preventDefault()}>
        <label>Estación</label>
        <select value={estacion} onChange={(e) => setEstacion(e.target.value)}>
          <option value="3195">Madrid, Retiro (IDEMA: 3195)</option>
        </select>

        <label>Fecha</label>
        <input
          type="date"
          value={fecha}
          onChange={(e) => setFecha(e.target.value)}
          max={getMaxFecha()}
        />

        <button type="button" onClick={handlePredict} disabled={cargando}>
          {cargando ? "Cargando..." : "Predecir"}
        </button>

        <button type="button" onClick={handleConsultar} disabled={cargando}>
          {cargando ? "Cargando..." : "Consultar histórico"}
        </button>
      </form>

      {resultado && (
        <div className="resultado">
          <h2>
            Resultado para <strong>{resultado.fecha}</strong> ({resultado.estacion}):
          </h2>
          <ul>
            <li>🌡️ Temp. media: {resultado.tmed} °C</li>
            <li>🔼 Temp. máx: {resultado.tmax} °C</li>
            <li>🔽 Temp. mín: {resultado.tmin} °C</li>
            <li>🌧 Precipitación: {resultado.prec} mm</li>
          </ul>
        </div>
      )}

      {error && <div className="error">{error}</div>}

      <p className="aviso-aemet">
        Debido a la demora habitual en la publicación de los datos oficiales por parte de AEMET (hasta 3 días),
        las predicciones se generan a partir del último día con información disponible. Esto podría reducir la
        precisión en contextos de alta variabilidad meteorológica.
      </p>
    </div>
  );
}

export default App;
