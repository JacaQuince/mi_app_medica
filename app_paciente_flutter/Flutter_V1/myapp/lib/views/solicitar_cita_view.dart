import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:myapp/services/sesion_usuario.dart';

class SolicitarCitaView extends StatefulWidget {
  const SolicitarCitaView({super.key});

  @override
  State<SolicitarCitaView> createState() => _SolicitarCitaViewState();
}

class _SolicitarCitaViewState extends State<SolicitarCitaView> {
  final _formKey = GlobalKey<FormState>();

  DateTime? _fechaSeleccionada;
  TimeOfDay? _horaSeleccionada;
  String? _especialidad;
  String? _doctorSeleccionado;
  List<String> _doctoresDisponibles = [];

  final supabase = Supabase.instance.client;

  @override
  void initState() {
    super.initState();
    _cargarDoctores();
  }

  Future<void> _cargarDoctores() async {
    try {
      final response = await supabase
          .from('usuarios')
          .select('nombre')
          .eq('rol', 'medico');

      final nombres = List<String>.from(response.map((e) => e['nombre']));
      setState(() {
        _doctoresDisponibles = nombres;
      });
    } catch (e) {
      print('❌ Error al obtener doctores: $e');
    }
  }

  Future<void> _enviarSolicitud() async {
    if (_formKey.currentState!.validate() &&
        _fechaSeleccionada != null &&
        _horaSeleccionada != null &&
        _doctorSeleccionado != null) {
      try {
        // 🔎 Obtener el paciente_id según el usuario logueado
        int? usuarioId = SesionUsuario.verificarSesion(context);
        if (usuarioId == null) return;

        // 🔍 Buscar el paciente con ese usuario_id
        final paciente = await SesionUsuario.obtenerPaciente(
          context,
          usuarioId,
        );
        if (paciente == null) return;

        final pacienteID = paciente['id'];
        final fecha = _fechaSeleccionada!.toIso8601String().split('T').first;
        final hora = _horaSeleccionada!.format(context);

        // 🔎 Verificar si ya hay una cita para esa fecha, hora y doctor
        final citaExistente =
            await supabase
                .from('citas')
                .select()
                .eq('fecha', fecha)
                .eq('hora', hora)
                .eq('doctor', _doctorSeleccionado!)
                .maybeSingle();

        if (citaExistente != null) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Ya existe una cita para ese doctor a esa hora'),
            ),
          );
          return;
        }

        // ✅ Insertar nueva cita
        await supabase.from('citas').insert({
          'fecha': fecha,
          'hora': hora,
          'especialidad': _especialidad,
          'doctor': _doctorSeleccionado,
          'paciente_id': pacienteID,
        });

        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('✅ Cita solicitada correctamente')),
        );

        Navigator.pop(context);
      } catch (e) {
        print('❌ Error al solicitar cita: $e');
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('Error al solicitar la cita')),
        );
      }
    } else {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Por favor completa todos los campos')),
      );
    }
  }

  Future<void> _seleccionarFecha() async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now(),
      lastDate: DateTime.now().add(const Duration(days: 365)),
    );
    if (picked != null) {
      setState(() {
        _fechaSeleccionada = picked;
      });
    }
  }

  Future<void> _seleccionarHora() async {
    final TimeOfDay? picked = await showTimePicker(
      context: context,
      initialTime: TimeOfDay.now(),
    );
    if (picked != null) {
      setState(() {
        _horaSeleccionada = picked;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Solicitar Cita Médica')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              // Fecha
              ListTile(
                title: Text(
                  _fechaSeleccionada == null
                      ? 'Selecciona una fecha'
                      : 'Fecha: ${_fechaSeleccionada!.toLocal().toString().split(' ')[0]}',
                ),
                trailing: const Icon(Icons.calendar_today),
                onTap: _seleccionarFecha,
              ),

              // Hora
              ListTile(
                title: Text(
                  _horaSeleccionada == null
                      ? 'Selecciona una hora'
                      : 'Hora: ${_horaSeleccionada!.format(context)}',
                ),
                trailing: const Icon(Icons.access_time),
                onTap: _seleccionarHora,
              ),

              const SizedBox(height: 16),

              // Especialidad
              TextFormField(
                decoration: const InputDecoration(
                  labelText: 'Especialidad',
                  border: OutlineInputBorder(),
                ),
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'Campo requerido';
                  }
                  return null;
                },
                onChanged: (value) => _especialidad = value,
              ),

              const SizedBox(height: 16),

              // Doctor
              DropdownButtonFormField<String>(
                decoration: const InputDecoration(
                  labelText: 'Selecciona un doctor',
                  border: OutlineInputBorder(),
                ),
                value: _doctorSeleccionado,
                items:
                    _doctoresDisponibles.map((doctor) {
                      return DropdownMenuItem<String>(
                        value: doctor,
                        child: Text(doctor),
                      );
                    }).toList(),
                onChanged: (value) {
                  setState(() {
                    _doctorSeleccionado = value;
                  });
                },
                validator:
                    (value) => value == null ? 'Selecciona un doctor' : null,
              ),

              const SizedBox(height: 24),

              // Botón
              ElevatedButton.icon(
                onPressed: _enviarSolicitud,
                icon: const Icon(Icons.send),
                label: const Text('Solicitar Cita'),
                style: ElevatedButton.styleFrom(
                  minimumSize: const Size.fromHeight(50),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
