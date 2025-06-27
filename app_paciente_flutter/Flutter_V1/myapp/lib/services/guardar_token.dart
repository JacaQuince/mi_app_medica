import 'package:supabase_flutter/supabase_flutter.dart';
import 'fcm_service.dart';

class TokenFCMService {
  static Future<void> guardarToken(String usuarioId) async {
    try {
      final token = await FCMService.getToken();
      if (token == null || usuarioId.isEmpty) return;

      final supabase = Supabase.instance.client;

      final existing =
          await supabase
              .from('tokens_fcm')
              .select()
              .eq('usuario_id', usuarioId)
              .maybeSingle();

      if (existing == null) {
        await supabase.from('tokens_fcm').insert({
          'usuario_id': usuarioId,
          'token': token,
        });
        print('✅ Token insertado correctamente');
      } else {
        await supabase
            .from('tokens_fcm')
            .update({'token': token})
            .eq('usuario_id', usuarioId);
        print('✅ Token actualizado correctamente');
      }
    } catch (e, stackTrace) {
      print('❌ Error al guardar el token FCM: $e');
      print('🪵 StackTrace: $stackTrace');
    }
  }
}
