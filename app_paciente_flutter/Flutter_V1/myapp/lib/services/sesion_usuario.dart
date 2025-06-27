import 'package:flutter/material.dart';
import 'package:supabase_flutter/supabase_flutter.dart';

class SesionUsuario {
  static int? idUsuario;

  /// Verifica si hay sesión activa. Si no, muestra un mensaje.
  static int? verificarSesion(BuildContext context) {
    if (idUsuario == null) {
      ScaffoldMessenger.of(
        context,
      ).showSnackBar(const SnackBar(content: Text('No hay sesión activa')));
      return null;
    }
    return idUsuario;
  }

  /// Obtiene el paciente relacionado al usuarioId. Muestra mensaje si no existe.
  static Future<Map<String, dynamic>?> obtenerPaciente(
    BuildContext context,
    int usuarioId,
  ) async {
    final supabase = Supabase.instance.client;

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
      return null;
    }

    return paciente;
  }
}
