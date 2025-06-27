import 'package:flutter/material.dart';

class MedicamentosView extends StatefulWidget {
  const MedicamentosView({super.key});

  @override
  State<MedicamentosView> createState() => _MedicamentosViewState();
}

class _MedicamentosViewState extends State<MedicamentosView> {
  // 📥 Lista simulada de medicamentos asignados al paciente
  final List<Map<String, dynamic>> _medicamentos = [
    {'nombre': 'Paracetamol 500mg', 'hora': '08:00 AM', 'tomado': false},
    {'nombre': 'Ibuprofeno 400mg', 'hora': '02:00 PM', 'tomado': false},
    {'nombre': 'Amoxicilina 250mg', 'hora': '08:00 PM', 'tomado': false},
  ];

  void _confirmarToma() {
    final tomados = _medicamentos.where((m) => m['tomado'] == true).toList();

    // 🛠 Aquí se conectará con Supabase para registrar que se tomó el medicamento
    print(
      '🗂 Medicamentos tomados: ${tomados.map((e) => e['nombre']).toList()}',
    );

    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Toma confirmada correctamente')),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Mis Medicamentos')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            const Text(
              'Marca los medicamentos que ya tomaste hoy:',
              style: TextStyle(fontSize: 16),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: ListView.builder(
                itemCount: _medicamentos.length,
                itemBuilder: (context, index) {
                  final med = _medicamentos[index];
                  return Card(
                    child: CheckboxListTile(
                      title: Text(med['nombre']),
                      subtitle: Text('Hora: ${med['hora']}'),
                      value: med['tomado'],
                      onChanged: (value) {
                        setState(() {
                          med['tomado'] = value;
                        });
                      },
                    ),
                  );
                },
              ),
            ),
            ElevatedButton.icon(
              onPressed: _confirmarToma,
              icon: const Icon(Icons.check),
              label: const Text('Confirmar toma'),
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
