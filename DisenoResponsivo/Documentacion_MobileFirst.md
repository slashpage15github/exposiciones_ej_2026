# Documentación Técnica: Mobile First & Media Queries

> Basado en la demostración de la carpeta `Presentacion/`

## 1. ¿Qué es Mobile First?

**Concepto:**
"Mobile First" (Móvil Primero) no es solo una técnica de código, es una filosofía de diseño. Significa que empezamos diseñando y programando para la pantalla más pequeña (celular) y luego vamos agregando complejidad a medida que la pantalla crece.

**En tu código (`Presentacion/style.css`):**
Fíjate en las primeras 42 líneas de tu CSS. Esas reglas aplican a **todos** los dispositivos por defecto.

```css
/* Esto es lo que ve el celular por defecto */
.col {
  width: 100%;       /* Ocupa todo el ancho */
  margin-bottom: .7rem; /* Se apila uno debajo del otro */
}
```

**¿Por qué lo hacemos así?**

1. **Rendimiento:** Los celulares suelen tener procesadores más lentos y conexiones inestables. Al cargar el CSS base primero (sin queries complejas), la página se renderiza más rápido.
2. **Flujo Natural:** Los elementos HTML (`div`, `p`, `h1`) son bloques por naturaleza. Se apilan verticalmente. Mobile First aprovecha este comportamiento natural, por lo que escribimos menos código.

---

## 2. ¿Qué son las Media Queries?

**Concepto:**
Son "condicionales" (como un `if` en programación) que nos permiten aplicar estilos CSS **solo** si se cumplen ciertas condiciones, como el ancho de la pantalla.

**Sintaxis:**

```css
@media (condición) {
  /* Reglas CSS que solo aplican si se cumple la condición */
}
```

---

## 3. Explicación de tus Puntos de Quiebre (Breakpoints)

En tu archivo `style.css`, utilizaste una estructura escalonada perfecta. Vamos a analizar qué pasa en cada etapa.

### Estado Base (Móvil - 0rem hasta 47.9rem)

* **Color de fondo:** `#f1f1f1` (Gris claro)
* **Layout:** Bloques apilados verticalmente (debido al comportamiento por defecto de `.col` y la falta de `display: flex` en `.row`).

### Punto de Quiebre 1: Tablet (`min-width: 48rem`)

```css
@media (min-width: 48rem) {
  .row {
    display: flex;       /* Activamos columnas */
    flex-direction: row; /* Elementos uno al lado del otro */
  }
  body { background-color: #74ff03; } /* Verde Lima */
}
```

* **Lo que sucede:** Cuando la pantalla supera los ~768px, el diseño "salta". Los bloques que estaban apilados ahora se ponen en fila horizontal.
* **Visual:** El fondo cambia a verde para indicar visualmente que entramos en modo "Tablet".

### Punto de Quiebre 2: Escritorio (`min-width: 64rem`)

```css
@media (min-width: 64rem) {
  .row {
    flex-direction: column; /* ¡Cambio interesante! */
  }
  body { background-color: #ffdd03; } /* Amarillo */
}
```

* **Lo que sucede:** Al llegar a ~1024px (Laptops), decidiste volver a apilarlos (`column`). Esto es útil a veces en diseños tipo "dashboard" o barras laterales.
* **Visual:** El fondo cambia a amarillo.

### Punto de Quiebre 3: Pantalla Grande (`min-width: 80rem`)

```css
@media (min-width: 80rem) {
  .row {
    flex-direction: row; /* Volvemos a fila horizontal */
  }
  body { background-color: #03ffab; } /* Turquesa */
}
```

* **Lo que sucede:** En monitores grandes (~1280px+), volvemos a expandir el contenido horizontalmente para aprovechar el espacio extra.

---

## 4. Resumen Visual

| Dispositivo | Ancho (aprox) | Color Fondo | Comportamiento Flex |
| :--- | :--- | :--- | :--- |
| **Celular** | < 768px | Gris (#f1f1f1) | Bloque (Normal) |
| **Tablet** | ≥ 768px | Verde (#74ff03) | Fila (Row) |
| **Laptop** | ≥ 1024px | Amarillo (#ffdd03)| Columna (Column) |
| **Monitor** | ≥ 1280px | Turquesa (#03ffab)| Fila (Row) |

## 5. Conclusión Clave

Tu código demuestra perfectamente la **Evolución Progresiva**:

1. Empiezas con una base sólida y simple (Móvil).
2. Usas `min-width` para *agregar* cambios solo cuando hay espacio suficiente.
3. Nunca usas `max-width` para "arreglar" cosas en móvil; siempre construyes de pequeño a grande. ¡Esa es la manera profesional de hacerlo!
