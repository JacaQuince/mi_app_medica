import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'solicitar_cita_view.dart';
import 'package:myapp/services/sesion_usuario.dart';

class CitasView extends StatefulWidget {
  const CitasView({Key? key}) : super(key: key);

  @override
  State<CitasView> createState() => _CitasViewState();
}

class _CitasViewState extends State<CitasView> {
  List<dynamic> _citas = [];
  bool _cargando = true;

  @override
  void initState() {
    super.initState();
    _cargarCitasDelPaciente();
  }

  Future<void> _cargarCitasDelPaciente() async {
    final context = this.context;
    final supabase = Supabase.instance.client;

    int? usuarioId = SesionUsuario.verificarSesion(context);
    if (usuarioId == null) return;

    try {
      final paciente = await SesionUsuario.obtenerPaciente(context, usuarioId);
      if (paciente == null) return;

      final pacienteID = paciente['id'];

      final citas = await supabase
          .from('citas')
          .select()
          .eq('paciente_id', pacienteID)
          .eq('activo', true)
          .order('fecha', ascending: true);

      setState(() {
        _citas = citas;
        _cargando = false;
      });
    } catch (e) {
      print('❌ Error al cargar citas: $e');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Error al cargar las citas')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Citas Médicas')),
      body:
          _cargando
              ? const Center(child: CircularProgressIndicator())
              : _citas.isEmpty
              ? const Center(child: Text('No tienes citas registradas'))
              : ListView.builder(
                itemCount: _citas.length,
                padding: const EdgeInsets.all(16),
                itemBuilder: (context, index) {
                  final c = _citas[index];
                  return Card(
                    child: ListTile(
                      leading: const Icon(Icons.calendar_today),
                      title: Text('${c['fecha']} - ${c['hora']}'),
                      subtitle: Text(c['doctor']),
                      trailing: const Icon(Icons.arrow_forward_ios),
                    ),
                  );
                },
              ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (context) => const SolicitarCitaView()),
          ).then((_) {
            // 🔄 Refrescar al volver
            _cargarCitasDelPaciente();
          });
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
