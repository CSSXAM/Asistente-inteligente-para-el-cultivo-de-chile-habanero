
import { useEffect, useState } from 'react'

function App() {
  const [mensaje, setMensaje] = useState('Conectando con FastAPI...')

  useEffect(() => {
    fetch('http://127.0.0.1:8000/')
      .then((respuesta) => {
        if (!respuesta.ok) {
          throw new Error('Error en la respuesta del servidor')
        }
        return respuesta.json()
      })
      .then((datos) => setMensaje(datos.mensaje))
      .catch(() => setMensaje('No se pudo conectar con FastAPI'))
  }, [])

  return (
    <main>
      <h1>Asistente IA para el cultivo de chile habanero</h1>
      <p>{mensaje}</p>
    </main>
  )
}

export default App
