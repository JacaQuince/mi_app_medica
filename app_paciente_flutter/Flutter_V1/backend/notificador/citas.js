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
  const en1Hora = new Date(ahora.getTime() + 60 * 60 * 1000);
  const en10Min = new Date(ahora.getTime() + 10 * 60 * 1000);

  const formatoHora = (fecha) => fecha.toTimeString().slice(0, 8);

  return {
    fechaIso,
    horaActual: horaExacta,
    hora1HoraAntes: formatoHora(en1Hora),
    hora10MinAntes: formatoHora(en10Min),
  };
}

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

async function verificarCitas() {
  const { fechaIso, hora1HoraAntes, hora10MinAntes, horaActual } = obtenerFechaHoraZona();
  console.log(`🔍 Verificando citas para ${fechaIso} a las ${hora1HoraAntes}, ${hora10MinAntes} y ${horaActual}`);

  try {
    const citasUrl = `${supabaseUrl}/rest/v1/citas?fecha=eq.${fechaIso}&activo=eq.true&select=id,hora,doctor,paciente_id,especialidad`;
    const { data: citas } = await axios.get(citasUrl, { headers });

    for (const cita of citas) {
      const horaCita = cita.hora;

      let mensaje = null;

      if (horaCita === hora1HoraAntes) {
        mensaje = `🕐 Tu cita con Dr.${cita.doctor} - ${cita.especialidad} es en 1 hora`;
      } else if (horaCita === hora10MinAntes) {
        mensaje = `⏰ Tu cita con Dr.${cita.doctor} - ${cita.especialidad} es en 10 minutos. ¡Prepárate!`;
      } else if (horaCita === horaActual) {
        mensaje = `📅 Es hora de tu cita con Dr.${cita.doctor} - ${cita.especialidad} ¡Acude a tu consulta!`;
      }

      if (mensaje) {
        const pacienteUrl = `${supabaseUrl}/rest/v1/pacientes?id=eq.${cita.paciente_id}&select=usuario_id`;
        const { data: pacientes } = await axios.get(pacienteUrl, { headers });

        if (pacientes.length === 0) continue;

        const usuarioId = pacientes[0].usuario_id;

        const tokensUrl = `${supabaseUrl}/rest/v1/tokens_fcm?usuario_id=eq.${usuarioId}&select=token`;
        const { data: tokens } = await axios.get(tokensUrl, { headers });

        if (tokens.length === 0) continue;

        const token = tokens[0].token;
        await enviarNotificacion(token, 'Recordatorio de Cita Médica', mensaje);
      }
    }
  } catch (err) {
    console.error('❌ Error en verificación de citas:', err.message);
    if (err.response) {
      console.error('🛠️ Supabase error data:', err.response.data);
      console.error('📋 Supabase status:', err.response.status);
    }
  }
}

cron.schedule('* * * * *', () => {
  console.log('🔄 Ejecutando verificación de citas...');
  verificarCitas();
});
