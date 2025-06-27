import 'package:flutter/material.dart';
import 'package:myapp/views/medicamentos_view.dart';
import 'package:supabase_flutter/supabase_flutter.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter_local_notifications/flutter_local_notifications.dart';

import 'views/login_view.dart';
import 'views/home_view.dart';
import 'views/register_view.dart';
import 'views/recordatorios_view.dart';
import 'views/signos_vitales_view.dart';
import 'views/citas_view.dart';
import 'views/historial_view.dart';
import 'views/solicitar_cita_view.dart';
import 'views/reportes_pdf_view.dart';

// Instancia global de FlutterLocalNotificationsPlugin
final FlutterLocalNotificationsPlugin flutterLocalNotificationsPlugin =
    FlutterLocalNotificationsPlugin();

Future<void> _firebaseMessagingBackgroundHandler(RemoteMessage message) async {
  await Firebase.initializeApp();
  print('🔔 Notificación en background: ${message.messageId}');
}

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Inicializar Supabase
  await Supabase.initialize(url: '', anonKey: '');

  // Inicializar Firebase
  await Firebase.initializeApp();

  // Inicializar Flutter Local Notifications
  const AndroidInitializationSettings initializationSettingsAndroid =
      AndroidInitializationSettings('@mipmap/ic_launcher');
  const InitializationSettings initializationSettings = InitializationSettings(
    android: initializationSettingsAndroid,
  );
  await flutterLocalNotificationsPlugin.initialize(initializationSettings);

  // Handler de notificaciones en background
  FirebaseMessaging.onBackgroundMessage(_firebaseMessagingBackgroundHandler);

  runApp(const MyApp());
}

class MyApp extends StatefulWidget {
  const MyApp({super.key});

  @override
  State<MyApp> createState() => _MyAppState();
}

class _MyAppState extends State<MyApp> {
  final FirebaseMessaging _messaging = FirebaseMessaging.instance;

  @override
  void initState() {
    super.initState();
    _setupFCM();
  }

  void _setupFCM() async {
    NotificationSettings settings = await _messaging.requestPermission();
    print('🔐 Permiso de notificación: ${settings.authorizationStatus}');

    String? token = await _messaging.getToken();
    print('📱 FCM Token: $token');

    // Escuchar mensajes en foreground y mostrar notificación local
    FirebaseMessaging.onMessage.listen((RemoteMessage message) {
      print('📲 Notificación en foreground: ${message.notification?.title}');
      _showNotification(message);
    });

    // Cuando se abre la notificación desde background
    FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
      print(
        '📬 Notificación abierta desde background: ${message.notification?.title}',
      );
      // Aquí puedes navegar a alguna pantalla si quieres
    });
  }

  Future<void> _showNotification(RemoteMessage message) async {
    RemoteNotification? notification = message.notification;
    AndroidNotification? android = message.notification?.android;

    if (notification != null && android != null) {
      const AndroidNotificationDetails androidDetails =
          AndroidNotificationDetails(
            'canal_principal',
            'Notificaciones importantes',
            importance: Importance.max,
            priority: Priority.high,
          );
      const NotificationDetails platformDetails = NotificationDetails(
        android: androidDetails,
      );

      await flutterLocalNotificationsPlugin.show(
        notification.hashCode,
        notification.title,
        notification.body,
        platformDetails,
        payload: message.data['payload'], // opcional
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'App Salud',
      debugShowCheckedModeBanner: false,
      initialRoute: '/',
      routes: {
        '/': (context) => const LoginView(),
        '/home': (context) => const HomeView(),
        '/register': (context) => const RegisterView(),
        '/recordatorios': (context) => const RecordatoriosView(),
        '/signos-vitales': (context) => const SignosVitalesView(),
        '/citas': (context) => const CitasView(),
        '/historial': (context) => const HistorialView(),
        '/medicamentos': (context) => const MedicamentosView(),
        '/solicitar-cita': (context) => const SolicitarCitaView(),
        '/reportes-pdf': (context) => const ReportesPDFView(),
      },
    );
  }
}
