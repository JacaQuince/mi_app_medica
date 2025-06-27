import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:myapp/services/sesion_usuario.dart';

class ConfirmacionTomaScreen extends StatefulWidget {
  const ConfirmacionTomaScreen({super.key});

  @override
  State<ConfirmacionTomaScreen> createState() => _ConfirmacionTomaScreenState();
}

class _ConfirmacionTomaScreenState extends State<ConfirmacionTomaScreen> {
  final supabase = Supabase.instance.client;
  List<Map<String, dynamic>> _tomas = [];
  bool _cargando = true;

  @override
  void initState() {
    super.initState();
    _cargarTomasPendientes();
  }

  Future<void> _cargarTomasPendientes() async {
    final usuarioId = SesionUsuario.verificarSesion(context);
    if (usuarioId == null) return;

    final paciente =
        await supabase
            .from('pacientes')
            .select('id')
            .eq('usuario_id', usuarioId)
            .maybeSingle();

    if (paciente == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('Paciente no encontrado')));
      return;
    }

    final pacienteID = paciente['id'];

    final data = await supabase
        .from('tomasmedicamentos')
        .select(
          'id, fecha, hora, confirmacion, medicamentos(nombre), citas!inner(activo)',
        )
        .eq('paciente_id', pacienteID)
        .eq('citas.activo', true)
        .order('fecha', ascending: true);

    setState(() {
      _tomas =
          data.map<Map<String, dynamic>>((e) {
            final DateTime fechaHoraToma = DateTime.parse(
              "${e['fecha']} ${e['hora']}",
            );
            final bool pasada = fechaHoraToma.isBefore(
              DateTime.now().subtract(const Duration(minutes: 5)),
            );

            return {
              'id': e['id'],
              'nombre': e['medicamentos']['nombre'],
              'fecha': e['fecha'],
              'hora': e['hora'],
              'confirmacion': e['confirmacion'],
              'deshabilitado': pasada,
            };
          }).toList();
      _cargando = false;
    });
  }

  Future<void> _actualizarConfirmacion(int id, bool confirmado) async {
    await supabase
        .from('tomasmedicamentos')
        .update({'confirmacion': confirmado})
        .eq('id', id);
  }

  @override
  Widget build(BuildContext context) {
    final DateFormat formatter = DateFormat('dd/MM/yyyy');

    return Scaffold(
      appBar: AppBar(title: const Text('Confirmar Toma de Medicamentos')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child:
            _cargando
                ? const Center(child: CircularProgressIndicator())
                : _tomas.isEmpty
                ? const Center(child: Text('No hay tomas disponibles.'))
                : ListView.builder(
                  itemCount: _tomas.length,
                  itemBuilder: (context, index) {
                    final med = _tomas[index];
                    final String fechaFormateada = formatter.format(
                      DateTime.parse(med['fecha']),
                    );

                    return Card(
                      child: CheckboxListTile(
                        title: Text(med['nombre']),
                        subtitle: Text(
                          'Fecha: $fechaFormateada\nHora: ${med['hora']}',
                        ),
                        value: med['confirmacion'],
                        onChanged:
                            med['deshabilitado']
                                ? null
                                : (value) async {
                                  setState(() {
                                    med['confirmacion'] = value!;
                                  });
                                  await _actualizarConfirmacion(
                                    med['id'],
                                    value!,
                                  );
                                },
                      ),
                    );
                  },
                ),
      ),
    );
  }
}
