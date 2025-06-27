import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:crypt/crypt.dart';

class RegisterView extends StatefulWidget {
  const RegisterView({super.key});

  @override
  State<RegisterView> createState() => _RegisterViewState();
}

class _RegisterViewState extends State<RegisterView> {
  final _nombreController = TextEditingController();
  final _telefonoController = TextEditingController();
  final _domicilioController = TextEditingController();
  final _correoController = TextEditingController();
  final _passwordController = TextEditingController();
  final supabase = Supabase.instance.client;

  bool _loading = false;
  String _error = '';

  Future<void> register() async {
    setState(() {
      _loading = true;
      _error = '';
    });

    try {
      final nombre = _nombreController.text.trim();
      final telefono = _telefonoController.text.trim();
      final domicilio = _domicilioController.text.trim();
      final email = _correoController.text.trim();
      final rawPassword = _passwordController.text.trim();

      // Validar que no exista usuario con ese correo
      final existing =
          await supabase
              .from('usuarios')
              .select('id')
              .eq('correo', email)
              .maybeSingle();

      if (existing != null) {
        setState(() {
          _error = 'El correo ya está registrado';
        });
        return;
      }

      // Hashear la contraseña con crypt
      final hashedPassword =
          Crypt.sha256(rawPassword, rounds: 10000).toString();

      // Insertar nuevo usuario en la tabla 'usuarios' y obtener el id generado
      final insertResponse =
          await supabase
              .from('usuarios')
              .insert({
                'nombre': nombre,
                'correo': email,
                'contraseña_hash': hashedPassword,
                'rol': 'paciente',
              })
              .select('id')
              .single();

      if (insertResponse['id'] == null) {
        setState(() {
          _error = 'No se pudo registrar el usuario';
        });
        return;
      }

      final int nuevoUsuarioId = insertResponse['id'];

      // Insertar en la tabla 'pacientes' con doctor_id = 1 por defecto
      final insertPaciente = await supabase.from('pacientes').insert({
        'nombre': nombre,
        'telefono': telefono,
        'domicilio': domicilio,
        'correo_electronico': email,
        'usuario_id': nuevoUsuarioId,
        'doctor_id': 1, // doctor_id fijo
      });

      if (insertPaciente.error != null) {
        setState(() {
          _error =
              'Error al registrar el paciente: ${insertPaciente.error!.message}';
        });
        return;
      }

      // Registro exitoso, navegar a login o home
      Navigator.pushReplacementNamed(context, '/login');
    } catch (e) {
      setState(() {
        _error = 'Error al registrar: ${e.toString()}';
      });
    } finally {
      setState(() {
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Registrarse')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: SingleChildScrollView(
          // Para evitar overflow
          child: Column(
            children: [
              TextField(
                controller: _nombreController,
                decoration: const InputDecoration(labelText: 'Nombre'),
              ),
              TextField(
                controller: _telefonoController,
                decoration: const InputDecoration(labelText: 'Teléfono'),
                keyboardType: TextInputType.phone,
              ),
              TextField(
                controller: _domicilioController,
                decoration: const InputDecoration(labelText: 'Domicilio'),
              ),
              TextField(
                controller: _correoController,
                decoration: const InputDecoration(labelText: 'Correo'),
                keyboardType: TextInputType.emailAddress,
              ),
              TextField(
                controller: _passwordController,
                decoration: const InputDecoration(labelText: 'Contraseña'),
                obscureText: true,
              ),
              const SizedBox(height: 20),
              if (_error.isNotEmpty)
                Text(_error, style: const TextStyle(color: Colors.red)),
              ElevatedButton(
                onPressed: _loading ? null : register,
                child:
                    _loading
                        ? const CircularProgressIndicator()
                        : const Text('Crear cuenta'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
