import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:myapp/services/sesion_usuario.dart';

class SignosVitalesView extends StatefulWidget {
  const SignosVitalesView({Key? key}) : super(key: key);

  @override
  State<SignosVitalesView> createState() => _SignosVitalesViewState();
}

class _SignosVitalesViewState extends State<SignosVitalesView> {
  final supabase = Supabase.instance.client;
  List<Map<String, dynamic>> _signos = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _cargarSignos();
  }

  Future<void> _cargarSignos() async {
    final context = this.context;

    setState(() => _isLoading = true);

    try {
      final usuarioId = SesionUsuario.verificarSesion(context);
      if (usuarioId == null) return;

      final paciente = await SesionUsuario.obtenerPaciente(context, usuarioId);
      if (paciente == null) return;

      final pacienteID = paciente['id'];

      final response = await supabase
          .from('signosvitales')
          .select()
          .eq('paciente_id', pacienteID)
          .order('fecha_hora', ascending: false);

      final data = response as List<dynamic>;

      setState(() {
        _signos =
            data
                .map<Map<String, dynamic>>((e) => Map<String, dynamic>.from(e))
                .toList();
      });
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('❌ Error cargando signos: $e')));
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _irARegistroSignos() async {
    final registrado = await Navigator.push(
      context,
      MaterialPageRoute(builder: (_) => const RegistrarSignoView()),
    );
    if (registrado == true) _cargarSignos();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Signos Vitales')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child:
            _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _signos.isEmpty
                ? const Center(
                  child: Text('No hay signos vitales registrados.'),
                )
                : ListView.builder(
                  itemCount: _signos.length,
                  itemBuilder: (context, index) {
                    final s = _signos[index];
                    final fechaHora = DateTime.tryParse(s['fecha_hora'] ?? '');
                    final fechaFormateada =
                        fechaHora != null
                            ? '${fechaHora.day}/${fechaHora.month}/${fechaHora.year} ${fechaHora.hour.toString().padLeft(2, '0')}:${fechaHora.minute.toString().padLeft(2, '0')}'
                            : 'Fecha desconocida';

                    return Card(
                      child: ListTile(
                        leading: const Icon(Icons.monitor_heart),
                        title: Text(s['tipo'] ?? 'Desconocido'),
                        subtitle: Text(
                          '${s['valor'] ?? '-'}\n$fechaFormateada',
                        ),
                        isThreeLine: true,
                      ),
                    );
                  },
                ),
      ),
      floatingActionButton: FloatingActionButton.extended(
        onPressed: _irARegistroSignos,
        icon: const Icon(Icons.add),
        label: const Text('Registrar nuevos signos'),
      ),
    );
  }
}

class RegistrarSignoView extends StatefulWidget {
  const RegistrarSignoView({Key? key}) : super(key: key);

  @override
  State<RegistrarSignoView> createState() => _RegistrarSignoViewState();
}

class _RegistrarSignoViewState extends State<RegistrarSignoView> {
  final supabase = Supabase.instance.client;
  final _valorController = TextEditingController();
  bool _isSaving = false;

  final List<String> _tipos = [
    'Presión arterial',
    'Frecuencia cardíaca',
    'Temperatura',
    'Oxigenación',
    'Frecuencia respiratoria',
  ];
  String? _tipoSeleccionado;

  Future<void> _guardarSigno() async {
    setState(() => _isSaving = true);

    try {
      final usuarioId = SesionUsuario.verificarSesion(context);
      if (usuarioId == null) return;

      final paciente = await SesionUsuario.obtenerPaciente(context, usuarioId);
      if (paciente == null) return;

      final pacienteId = paciente['id'];
      final tipo = _tipoSeleccionado ?? '';
      final valor = _valorController.text.trim();

      if (tipo.isEmpty || valor.isEmpty) {
        throw Exception('Todos los campos son obligatorios');
      }

      final now = DateTime.now().toIso8601String();

      await supabase.from('signosvitales').insert({
        'paciente_id': pacienteId,
        'tipo': tipo,
        'valor': valor,
        'fecha_hora': now,
      });

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('✅ Signo registrado exitosamente')),
      );
      Navigator.pop(context, true);
    } catch (e) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(SnackBar(content: Text('❌ Error al guardar: $e')));
    } finally {
      setState(() => _isSaving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registrar Signo Vital')),
      body: Padding(
        padding: const EdgeInsets.all(20),
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
              onChanged: (valor) => setState(() => _tipoSeleccionado = valor),
              decoration: const InputDecoration(
                labelText: 'Tipo de signo vital',
              ),
            ),
            TextField(
              controller: _valorController,
              decoration: const InputDecoration(
                labelText: 'Valor (ej. 120/80)',
              ),
            ),
            const SizedBox(height: 20),
            ElevatedButton.icon(
              onPressed: _isSaving ? null : _guardarSigno,
              icon:
                  _isSaving
                      ? const SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                      : const Icon(Icons.save),
              label: Text(_isSaving ? 'Guardando...' : 'Guardar signo vital'),
              style: ElevatedButton.styleFrom(
                minimumSize: const Size.fromHeight(50),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
