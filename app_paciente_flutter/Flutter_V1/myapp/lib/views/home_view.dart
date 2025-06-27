import 'package:flutter/material.dart';
import 'package:myapp/services/guardar_token.dart';
import 'package:myapp/services/sesion_usuario.dart';
import 'package:myapp/views/confirmacion_toma_view.dart';

class HomeView extends StatefulWidget {
  const HomeView({Key? key}) : super(key: key);

  @override
  State<HomeView> createState() => _HomeViewState();
}

class _HomeViewState extends State<HomeView> {
  @override
  void initState() {
    super.initState();
    _guardarTokenFCM();
  }

  Future<void> _guardarTokenFCM() async {
    final usuarioId = SesionUsuario.idUsuario?.toString();
    if (usuarioId != null) {
      await TokenFCMService.guardarToken(usuarioId);
    } else {
      print('⚠️ No se encontró usuario logueado para guardar el token');
    }
  }

  void _goTo(BuildContext context, String routeName) {
    Navigator.pushNamed(context, routeName);
  }

  void _logout(BuildContext context) {
    SesionUsuario.idUsuario = null;
    Navigator.pushReplacementNamed(context, '/');
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bienvenido'),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () => _logout(context),
          ),
        ],
      ),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          const Text(
            'Resumen de Salud',
            style: TextStyle(fontSize: 22, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),

          // Card 1 - Próxima toma
          Card(
            elevation: 4,
            child: ListTile(
              leading: const Icon(Icons.alarm, color: Colors.blue),
              title: const Text('Próximas tomas de medicamentos'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ConfirmacionTomaScreen(),
                  ),
                );
              },
            ),
          ),

          const SizedBox(height: 12),

          // Card 2 - Signos vitales
          Card(
            elevation: 4,
            child: ListTile(
              leading: const Icon(Icons.favorite, color: Colors.red),
              title: const Text('Signos vitales'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => _goTo(context, '/signos-vitales'),
            ),
          ),

          const SizedBox(height: 12),

          // Card 3 - Cita médica próxima
          Card(
            elevation: 4,
            child: ListTile(
              leading: const Icon(Icons.calendar_today, color: Colors.green),
              title: const Text('Citas médicas'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => _goTo(context, '/citas'),
            ),
          ),

          const SizedBox(height: 12),

          // Card 4 - Historial de tomas
          Card(
            elevation: 4,
            child: ListTile(
              leading: const Icon(Icons.history, color: Colors.deepPurple),
              title: const Text('Historial de tomas'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => _goTo(context, '/historial'),
            ),
          ),

          const SizedBox(height: 12),

          // Card 5 - Reportes PDF
          Card(
            elevation: 4,
            child: ListTile(
              leading: const Icon(Icons.picture_as_pdf, color: Colors.orange),
              title: const Text('Reportes PDF'),
              trailing: const Icon(Icons.arrow_forward_ios),
              onTap: () => _goTo(context, '/reportes-pdf'),
            ),
          ),
        ],
      ),
    );
  }
}
