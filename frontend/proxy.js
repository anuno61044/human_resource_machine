import http from 'http';
import httpProxy from 'http-proxy';
import dgram from 'dgram'; // Para comunicación UDP (Multicast)

let targetHost = '10.0.11.2'; // Backend IP
const targetPort = 8000;
const multicastAddress = '224.0.0.1'; // Dirección Multicast
const multicastPort = 10000; // Puerto Multicast
const localPort = 8001; // Puerto para recibir la confirmación

const proxy = httpProxy.createProxyServer({});

// Función para enviar mensaje multicast y esperar confirmación
async function sendMulticastMessage(message) {
  return new Promise((resolve, reject) => {
    const client = dgram.createSocket({ type: 'udp4', reuseAddr: true });

    client.bind(localPort, () => {
      client.setBroadcast(true);
      client.setMulticastTTL(128);
      client.addMembership(multicastAddress);
    });

    // Enviar mensaje multicast
    const messageBuffer = Buffer.from(message);
    client.send(messageBuffer, multicastPort, multicastAddress, (err) => {
      if (err) {
        console.error('Error enviando multicast:', err);
        reject(err);
        client.close();
      } else {
        console.log(`Mensaje multicast enviado: ${message}`);
      }
    });

    // Escuchar confirmación
    let isResolved = false; // Variable para verificar si ya se resolvió
    client.on('message', (msg, rinfo) => {
      if (!isResolved) {
        console.log(`Confirmación recibida de ${rinfo.address}:${rinfo.port}: ${msg.toString()}`);
        client.close();
        isResolved = true; // Marcar como resuelto
        resolve(rinfo.address);
      }
    });

    // Timeout si no hay respuesta
    setTimeout(() => {
      if (!isResolved) {
        console.log('No se recibió confirmación del servidor multicast.');
        client.close();
        reject('No response');
      }
    }, 3000);
  });
}

const server = http.createServer(async (req, res) => {
  
  console.log(`url = ${targetHost}:${targetPort}`);
  console.log(`request = ${req.url}`);

  if (!req.multicastSent) {
    try {
      if (req.url !== '/favicon.ico') {
        console.log('***************************Nueva solicitud***************************');
        console.log(`URL : ${req.url}`);
      }

      // Enviar solicitud multicast antes de procesar
      const clientIp = process.env.CONTAINER_IP;
      console.log(`Enviando solicitud multicast con IP del cliente: ${clientIp}`);
      const server_ip = await sendMulticastMessage(`${clientIp}`);
      console.log('Confirmación recibida:', server_ip);
      targetHost = server_ip;
      
      req.multicastSent = true; // Marcar como enviada la solicitud multicast para esta petición
    } catch (error) {
      console.error('Error en la comunicación multicast:', error);
    }
  }

  proxy.web(req, res, { target: `http://${targetHost}:${targetPort}` }, (err) => {
    if (err) {
      console.error('Error al reenviar la solicitud:', err);
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('Error al reenviar la solicitud');
    }
  });
});

server.listen(8000, () => {
  console.log(`Proxy server escuchando en http://localhost:8000`);
});