import 'package:flutter/material.dart';

class RecordatoriosView extends StatelessWidget {
  const RecordatoriosView({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // 📝 Más adelante se conectará con Supabase para obtener recordatorios
    final recordatorios = [
      {'medicamento': 'Paracetamol', 'hora': '08:00 AM'},
      {'medicamento': 'Ibuprofeno', 'hora': '02:00 PM'},
    ];

    return Scaffold(
      appBar: AppBar(title: const Text('Recordatorios')),
      body: ListView.builder(
        itemCount: recordatorios.length,
        padding: const EdgeInsets.all(16),
        itemBuilder: (context, index) {
          final item = recordatorios[index];
          return Card(
            child: ListTile(
              leading: const Icon(Icons.medication),
              title: Text(item['medicamento']!),
              subtitle: Text('Hora: ${item['hora']}'),
              trailing: IconButton(
                icon: const Icon(Icons.check_circle, color: Colors.green),
                onPressed: () {
                  // 🚀 En el futuro navegará a confirmación de toma
                  Navigator.pushNamed(context, '/confirmacion-toma');
                },
              ),
            ),
          );
        },
      ),
    );
  }
}
