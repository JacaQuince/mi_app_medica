import 'package:firebase_messaging/firebase_messaging.dart';

FirebaseMessaging messaging = FirebaseMessaging.instance;

void setupInteractedMessage() async {
  NotificationSettings settings = await messaging.requestPermission();

  if (settings.authorizationStatus == AuthorizationStatus.authorized) {
    print('Permiso concedido');

    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      // Mostrar notificación en primer plano
    });

    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      // Acción al abrir notificación
    });
  }
}
