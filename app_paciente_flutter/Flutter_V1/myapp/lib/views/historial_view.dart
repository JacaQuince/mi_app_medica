import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:myapp/services/sesion_usuario.dart';

class HistorialView extends StatefulWidget {
  const HistorialView({Key? key}) : super(key: key);

  @override
  State<HistorialView> createState() => _HistorialViewState();
}

class _HistorialViewState extends State<HistorialView> {
  final supabase = Supabase.instance.client;
  List<Map<String, dynamic>> _historial = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _cargarHistorial();
  }

  Future<void> _cargarHistorial() async {
    setState(() => _isLoading = true);
    try {
      int? usuarioId = SesionUsuario.verificarSesion(context);
      if (usuarioId == null) return;
      // 🔍 Buscar el paciente con ese usuario_id
      final paciente = await SesionUsuario.obtenerPaciente(context, usuarioId);
      if (paciente == null) return;
      final pacienteID = paciente['id'];

      if (pacienteID == null) return;

      final response = await supabase
          .from('vista_medicamentos_por_cita')
          .select()
          .eq('paciente_id', pacienteID)
          .eq('confirmacion', true)
          .order('fecha_toma', ascending: false)
          .order('hora_toma', ascending: false);

      final data = response as List<dynamic>;

      setState(() {
        _historial =
            data
                .map<Map<String, dynamic>>((e) => Map<String, dynamic>.from(e))
                .toList();
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('Error cargando historial: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Historial de Tomas')),
      body:
          _isLoading
              ? const Center(child: CircularProgressIndicator())
              : _historial.isEmpty
              ? const Center(child: Text('No hay registros de tomas.'))
              : ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: _historial.length,
                itemBuilder: (context, index) {
                  final h = _historial[index];
                  final fecha = h['fecha_toma'] ?? 'Fecha desconocida';
                  final hora = h['hora_toma'] ?? 'Hora desconocida';
                  final medicamento =
                      h['medicamento'] ?? 'Medicamento desconocido';

                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.history),
                      title: Text(medicamento),
                      subtitle: Text('$fecha - $hora'),
                    ),
                  );
                },
              ),
    );
  }
}
