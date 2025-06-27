const admin = require('firebase-admin');
const serviceAccount = require('./fcm-service-account.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

// Función para enviar notificación FCM
async function enviarNotificacion(token, titulo, cuerpo) {
  const message = {
    token,
    notification: {
      title: titulo,
      body: cuerpo,
    },
  };

  try {
    const response = await admin.messaging().send(message);
    console.log('✅ Notificación enviada correctamente:', response);
  } catch (error) {
    console.error('❌ Error al enviar notificación:', error.message);
  }
}

// Ejecutar prueba manual (REEMPLAZA por tu token real de FCM)
(async () => {
  await enviarNotificacion(
    'Key',
    '🔔 Notificación de prueba',
    '¿Llegó esta notificación a tu dispositivo?'
  );
})();
