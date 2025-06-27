import 'package:flutter/material.dart';
import 'package:printing/printing.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:pdf/pdf.dart';

pw.Document generarPdfReporte(String tipo, List<Map<String, dynamic>> datos) {
  final pdf = pw.Document();

  String titulo = '';
  List<pw.Widget> contenido = [];

  if (tipo == 'Signos vitales') {
    titulo = 'Reporte de Signos Vitales';
    for (var item in datos) {
      final fechaHora = DateTime.tryParse(item['fecha_hora'] ?? '');
      final formatoFecha =
          fechaHora != null
              ? '${fechaHora.day}/${fechaHora.month}/${fechaHora.year} '
                  '${fechaHora.hour.toString().padLeft(2, '0')}:'
                  '${fechaHora.minute.toString().padLeft(2, '0')}'
              : 'Fecha desconocida';

      contenido.add(
        pw.Text(
          '[SV] [$formatoFecha] ${item['tipo']}: ${item['valor']}',
          style: pw.TextStyle(fontSize: 14),
        ),
      );
      contenido.add(pw.SizedBox(height: 4));
    }
  } else if (tipo == 'Tomas de medicamentos') {
    titulo = 'Reporte de Tomas de Medicamentos';
    for (var item in datos) {
      final confirmado = item['confirmacion'] == true ? 'O' : 'X';
      contenido.add(
        pw.Text(
          '[MED] [${item['fecha_toma'] ?? '-'} ${item['hora_toma'] ?? '-'}] '
          '${item['medicamento']} (${item['ingrediente_activo']}) - $confirmado',
          style: pw.TextStyle(fontSize: 14),
        ),
      );
      contenido.add(pw.SizedBox(height: 4));
    }
  } else if (tipo == 'Citas médicas') {
    titulo = 'Reporte de Citas Médicas';
    for (var item in datos) {
      final diagnostico = item['diagnostico'] ?? 'sin diagnóstico';
      contenido.add(
        pw.Text(
          '[CITA] [${item['fecha'] ?? '-'} ${item['hora'] ?? '-'}] '
          '${item['especialidad'] ?? '-'} - $diagnostico',
          style: pw.TextStyle(fontSize: 14),
        ),
      );
      contenido.add(pw.SizedBox(height: 4));
    }
  } else {
    titulo = 'Reporte';
    contenido.add(
      pw.Text('No hay datos disponibles', style: pw.TextStyle(fontSize: 14)),
    );
  }

  pdf.addPage(
    pw.Page(
      pageFormat: PdfPageFormat.a4,
      margin: const pw.EdgeInsets.all(20),
      build: (context) {
        return pw.Column(
          crossAxisAlignment: pw.CrossAxisAlignment.start,
          children: [
            pw.Text(
              titulo,
              style: pw.TextStyle(fontSize: 24, fontWeight: pw.FontWeight.bold),
            ),
            pw.SizedBox(height: 20),
            ...contenido,
          ],
        );
      },
    ),
  );

  return pdf;
}

Future<void> generarPdfDesdeDatos(
  BuildContext context,
  String tipo,
  List<Map<String, dynamic>> datos,
) async {
  if (datos.isEmpty) {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('No hay datos para generar el reporte PDF.'),
      ),
    );
    return;
  }

  final pdf = generarPdfReporte(tipo, datos);

  await Printing.layoutPdf(onLayout: (format) async => pdf.save());
}
