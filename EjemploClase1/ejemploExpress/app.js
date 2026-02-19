const express = require('express');
const app = express();
const port = 3001;

// Middleware para que Express entienda JSON (útil para APIs)
app.use(express.json());

// Ruta principal (GET)
app.get('/', (req, res) => {
  res.send('¡Hola Mundo desde Express!');
});

// Ejemplo de ruta con parámetros (GET)
app.get('/usuario/:nombre', (req, res) => {
  const nombre = req.params.nombre;
  res.json({ mensaje: `Hola, ${nombre}! Bienvenido a la API.` });
});

// Iniciar el servidor
app.listen(port, () => {
  console.log(`Servidor corriendo en http://localhost:${port}`);
});