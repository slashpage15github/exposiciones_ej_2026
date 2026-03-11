<?php
require('fpdf186/fpdf.php');

function convertirTexto($texto) {
    return iconv('UTF-8', 'windows-1252//TRANSLIT', (string)$texto); #Se cambia aquí para convertir lo que se recibe
}

// Conexión a la base de datos
$conexion = new mysqli("localhost", "root", "sistemas11", "test");

// Verificar conexión
if ($conexion->connect_error) {
    die("Error de conexión: " . $conexion->connect_error);
}

// Asegurar UTF-8 en MySQL
$conexion->set_charset("utf8");
 
// Consulta de datos
$sql = "SELECT municipio, COUNT(*) AS total #Se cambia aqui, porque es nuestra consulta
        FROM edificios_escolares
        GROUP BY municipio
        ORDER BY total DESC 
        Limit 50";


$resultado = $conexion->query($sql);

// Obtener total de registros
$total = $conexion->query("SELECT COUNT(*) AS total FROM edificios_escolares");
$total_registros = $total->fetch_assoc()['total'];

// Crear PDF
$pdf = new FPDF();
$pdf->AddPage();

// Título
$pdf->SetFont('Arial', 'B', 16);
$pdf->Cell(190, 10, 'Reporte de Edificios Escolares', 0, 1, 'C');
$pdf->Ln(5);

// Información general
$pdf->SetFont('Arial', '', 12);
$pdf->Cell(190, 10, 'Total de registros en la base de datos: ' . $total_registros, 0, 1);
$pdf->Ln(5);

// Encabezados
$pdf->SetFont('Arial', 'B', 12); #Se cambia aquí porque son los encabezados que pide nuestra consulta
$pdf->Cell(120, 10, 'Municipio', 1, 0, 'C');
$pdf->Cell(70, 10, 'Total de registros', 1, 1, 'C');
$pdf->Ln();

// Datos
$pdf->SetFont('Arial', '', 9);

while ($fila = $resultado->fetch_assoc()) {
    $pdf->Cell(120, 10, convertirTexto($fila['municipio']), 1, 0);
    $pdf->Cell(70, 10, $fila['total'], 1, 1, 'C');
}

// Salida del PDF
$pdf->Output();

$conexion->close();
?>