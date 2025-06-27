import 'package:flutter/material.dart';
import 'package:myapp/services/sesion_usuario.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:myapp/services/generarPdf.dart';

class ReportesPDFView extends StatefulWidget {
  const ReportesPDFView({Key? key}) : super(key: key);

  @override
  State<ReportesPDFView> createState() => _ReportesPDFViewState();
}

class _ReportesPDFViewState extends State<ReportesPDFView> {
  String _tipoSeleccionado = 'Signos vitales';
  List<Map<String, dynamic>> _datos = [];
  bool _isLoading = false;

  final List<String> _tipos = [
    'Signos vitales',
    'Tomas de medicamentos',
    'Citas médicas',
  ];

  Future<void> _cargarDatos() async {
    final context = this.context;
    setState(() => _isLoading = true);

    try {
      // Validar sesión
      int? usuarioId = SesionUsuario.verificarSesion(context);
      if (usuarioId == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('⚠️ Usuario no autenticado.')),
        );
        return;
      }

      // Obtener datos del paciente asociado
      final paciente = await SesionUsuario.obtenerPaciente(context, usuarioId);
      if (paciente == null) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('⚠️ No se encontró información del paciente.'),
          ),
        );
        return;
      }

      final pacienteID = paciente['id'];
      late final List<dynamic> response;

      final client = Supabase.instance.client;

      if (_tipoSeleccionado == 'Signos vitales') {
        response = await client
            .from('vista_signos_paciente')
            .select()
            .eq('paciente_id', pacienteID)
            .order('fecha_hora', ascending: false);
      } else if (_tipoSeleccionado == 'Tomas de medicamentos') {
        response = await client
            .from('vista_medicamentos_por_cita')
            .select()
            .eq('paciente_id', pacienteID)
            .not('fecha_toma', 'is', null)
            .order('fecha_toma', ascending: false);
      } else {
        response = await client
            .from('vista_citas_paciente')
            .select()
            .eq('paciente_id', pacienteID)
            .order('fecha', ascending: false);
      }

      setState(() {
        _datos =
            response
                .map<Map<String, dynamic>>((e) => Map<String, dynamic>.from(e))
                .toList();
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('❌ Error al cargar datos: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Widget _buildItem(Map<String, dynamic> item) {
    if (_tipoSeleccionado == 'Signos vitales') {
      final fechaHora = DateTime.tryParse(item['fecha_hora'] ?? '');
      final formato =
          fechaHora != null
              ? '${fechaHora.day}/${fechaHora.month}/${fechaHora.year} ${fechaHora.hour.toString().padLeft(2, '0')}:${fechaHora.minute.toString().padLeft(2, '0')}'
              : 'Fecha desconocida';
      return ListTile(
        leading: const Icon(Icons.monitor_heart, color: Colors.red),
        title: Text('[$formato] - ${item['tipo']}: ${item['valor']}'),
      );
    } else if (_tipoSeleccionado == 'Tomas de medicamentos') {
      final confirmado = item['confirmacion'] == true ? 'O' : 'X';
      return ListTile(
        leading: const Icon(Icons.medication, color: Colors.blue),
        title: Text(
          '[${item['fecha_toma'] ?? '-'} - ${item['hora_toma'] ?? '-'}] - ${item['medicamento']} (${item['ingrediente_activo']}) - $confirmado',
        ),
      );
    } else {
      final diagnostico = item['diagnostico'] ?? 'sin diagnóstico';
      return ListTile(
        leading: const Icon(Icons.calendar_today, color: Colors.green),
        title: Text(
          '[${item['fecha']} - ${item['hora']}] - ${item['especialidad']} - $diagnostico',
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reportes PDF')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            DropdownButtonFormField<String>(
              value: _tipoSeleccionado,
              items:
                  _tipos
                      .map(
                        (tipo) =>
                            DropdownMenuItem(value: tipo, child: Text(tipo)),
                      )
                      .toList(),
              onChanged: (valor) {
                setState(() => _tipoSeleccionado = valor!);
              },
              decoration: const InputDecoration(
                labelText: 'Selecciona un tipo de reporte',
                border: OutlineInputBorder(),
              ),
            ),
            const SizedBox(height: 12),

            // Botón para cargar y visualizar datos
            ElevatedButton.icon(
              onPressed: _cargarDatos,
              icon: const Icon(Icons.visibility),
              label: const Text('Visualizar informe'),
            ),

            const SizedBox(height: 12),

            // Botón para exportar a PDF - SOLO habilitado si hay datos
            ElevatedButton.icon(
              onPressed:
                  _datos.isNotEmpty
                      ? () => generarPdfDesdeDatos(
                        context,
                        _tipoSeleccionado,
                        _datos,
                      )
                      : null,
              icon: const Icon(Icons.picture_as_pdf),
              label: const Text('Exportar a PDF'),
            ),

            const SizedBox(height: 16),

            Expanded(
              child:
                  _isLoading
                      ? const Center(child: CircularProgressIndicator())
                      : _datos.isEmpty
                      ? const Center(child: Text('No hay datos para mostrar.'))
                      : ListView.builder(
                        itemCount: _datos.length,
                        itemBuilder:
                            (context, index) =>
                                Card(child: _buildItem(_datos[index])),
                      ),
            ),
          ],
        ),
      ),
    );
  }
}
