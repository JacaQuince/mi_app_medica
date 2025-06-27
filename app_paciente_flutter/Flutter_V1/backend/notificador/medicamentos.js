const cron = require('node-cron');
const axios = require('axios');
const admin = require('firebase-admin');
require('dotenv').config();

const serviceAccount = require('./fcm-service-account.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
});

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_API_KEY;

const headers = {
  apikey: supabaseKey,
  Authorization: `Bearer ${supabaseKey}`,
};

function obtenerFechaHoraZona() {
  const timeZone = 'America/Mazatlan';

  const formatter = new Intl.DateTimeFormat('en-US', {
    timeZone,
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  });

  const parts = formatter.formatToParts(new Date());
  const get = (type) => parts.find(p => p.type === type)?.value;

  const fechaIso = `${get('year')}-${get('month')}-${get('day')}`;
  const horaExacta = `${get('hour')}:${get('minute')}:${get('second')}`;

  const ahora = new Date(`${fechaIso}T${horaExacta}`);
  const cincoMin = new Date(ahora.getTime() + 5 * 60 * 1000);
  const hora5Min = cincoMin.toTimeString().slice(0, 8);

  console.log(`📍 Zona horaria: ${timeZone} | Fecha: ${fechaIso} | Hora: ${horaExacta}`);

  return { fechaIso, horaExacta, hora5Min };
}

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
    await admin.messaging().send(message);
    console.log('✅ Notificación enviada:', cuerpo);
  } catch (error) {
    console.error('❌ Error al enviar notificación:', error.message);
  }
}

// Función que se ejecuta cada minuto
async function verificarTomas() {
  const { fechaIso, horaExacta, hora5Min } = obtenerFechaHoraZona();
  const momentoExacto = `${fechaIso} ${horaExacta}`;
  const momento5Min = `${fechaIso} ${hora5Min}`;
  try {

    // 2) Obtener pacientes con usuario_id, para cada paciente buscar tomas en la vista_medicamentos_por_cita
    const pacientesUrl = `${supabaseUrl}/rest/v1/pacientes?select=id,usuario_id`;
    //console.log('📡 Consultando pacientes:', pacientesUrl);

    const { data: pacientes } = await axios.get(pacientesUrl, { headers });

    for (const paciente of pacientes) {
      const tomasUrl = `${supabaseUrl}/rest/v1/vista_medicamentos_por_cita?paciente_id=eq.${paciente.id}&fecha_toma=eq.${fechaIso}&select=medicamento,hora_toma,fecha_toma`;
    
      const { data: tomas } = await axios.get(tomasUrl, { headers });

      //console.log(`📅 Fecha actual: ${fechaIso} | Hora exacta: ${horaExacta} | Hora +5 minutos: ${hora5Min}`);

      for (const toma of tomas) {
        const momentoToma = `${toma.fecha_toma} ${toma.hora_toma}`;        
        //console.log(`📅 Fecha toma: ${toma.fecha_toma} | Hora toma: ${toma.hora_toma}`);

        if (momentoToma === momentoExacto || momentoToma === momento5Min) {
          const tokensUrl = `${supabaseUrl}/rest/v1/tokens_fcm?usuario_id=eq.${paciente.usuario_id}&select=token`;

          const { data: tokens } = await axios.get(tokensUrl, { headers });

          if (tokens.length > 0) {
            const token = tokens[0].token;
            const mensaje = momentoToma === momento5Min
              ? `⏳ Toma tu medicamento en 5 minutos: ${toma.medicamento}`
              : `💊 Es hora de tomar: ${toma.medicamento}`;

            await enviarNotificacion(token, 'Recordatorio de Medicación', mensaje);
          } else {
            console.warn(`⚠️ No se encontró token para usuario_id: ${paciente.usuario_id}`);
          }
        }
      }
    }
  } catch (err) {
    console.error('❌ Error en verificación de tomas:', err.message);
    if (err.response) {
      console.error('🛠️ Supabase error data:', err.response.data);
      console.error('📋 Supabase status:', err.response.status);
    }
  }
}

cron.schedule('* * * * *', () => {
  console.log('🔄 Ejecutando verificación de tomas...');
  verificarTomas();
});
