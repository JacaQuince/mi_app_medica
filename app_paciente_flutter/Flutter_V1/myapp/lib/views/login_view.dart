import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:crypt/crypt.dart';
import 'package:myapp/services/sesion_usuario.dart';

class LoginView extends StatefulWidget {
  const LoginView({super.key});

  @override
  State<LoginView> createState() => _LoginViewState();
}

class _LoginViewState extends State<LoginView> {
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final supabase = Supabase.instance.client;

  bool _loading = false;
  String _errorMessage = '';

  Future<void> login() async {
    setState(() {
      _loading = true;
      _errorMessage = '';
    });

    try {
      final email = _emailController.text.trim();
      final password = _passwordController.text.trim();

      // Buscar usuario por correo
      final response =
          await supabase
              .from('usuarios')
              .select()
              .eq('correo', email)
              .maybeSingle(); // no .single(), usar maybeSingle para evitar excepción si no existe

      if (response == null) {
        // No se encontró usuario con ese correo
        setState(() {
          _errorMessage = 'Correo o contraseña incorrectos';
        });
        return;
      }

      final storedHash = response['contraseña_hash'] as String?;

      if (storedHash == null) {
        setState(() {
          _errorMessage = 'Error en los datos del usuario';
        });
        return;
      }

      // Verificar contraseña con bcrypt (crypt)
      final isValid = Crypt(storedHash).match(password);

      if (isValid) {
        SesionUsuario.idUsuario =
            response['id'] as int; // guardamos el id numérico
        Navigator.pushReplacementNamed(context, '/home');
      } else {
        setState(() {
          _errorMessage = 'Correo o contraseña incorrectos';
        });
      }
    } catch (e) {
      setState(() {
        _errorMessage = 'Error: ${e.toString()}';
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
      appBar: AppBar(title: const Text('Iniciar sesión')),
      body: Padding(
        padding: const EdgeInsets.all(20),
        child: Column(
          children: [
            TextField(
              controller: _emailController,
              decoration: const InputDecoration(labelText: 'Correo'),
              keyboardType: TextInputType.emailAddress,
            ),
            TextField(
              controller: _passwordController,
              decoration: const InputDecoration(labelText: 'Contraseña'),
              obscureText: true,
            ),
            const SizedBox(height: 20),
            if (_errorMessage.isNotEmpty)
              Text(_errorMessage, style: const TextStyle(color: Colors.red)),
            ElevatedButton(
              onPressed: _loading ? null : login,
              child:
                  _loading
                      ? const CircularProgressIndicator()
                      : const Text('Entrar'),
            ),
            TextButton(
              onPressed: () {
                Navigator.pushNamed(context, '/register');
              },
              child: const Text('¿No tienes cuenta? Regístrate aquí'),
            ),
          ],
        ),
      ),
    );
  }
}
