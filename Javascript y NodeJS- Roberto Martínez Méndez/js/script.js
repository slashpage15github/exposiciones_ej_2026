function sumar(sum1, sum2) {
    let resultado;
    resultado = sum1 + sum2;
    return resultado;
}

const boton = document.getElementById('btnSumar');

boton.addEventListener('click', function () {
    const n1 = parseFloat(document.getElementById('num1').value);
    const n2 = parseFloat(document.getElementById('num2').value);

    if (isNaN(n1) || isNaN(n2)) {
        alert("Ingresa dos números válidos.");
        return;
    }

    const resultadoFinal = sumar(n1, n2);

    document.getElementById('resultadoTexto').innerText = "El resultado es: " + resultadoFinal;
});