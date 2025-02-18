import http from 'http';
import httpProxy from 'http-proxy';
import dgram from 'dgram'; // Para comunicación UDP (Multicast)

let targetHosts = []; // Lista de servidores backend
const targetPort = 8000;
const multicastAddress = '224.0.0.1'; // Dirección Multicast
const multicastPort = 10000; // Puerto Multicast
const localPort = 8001; // Puerto para recibir confirmaciones

const proxy = httpProxy.createProxyServer({});

// Función para enviar mensaje multicast y esperar confirmaciones de múltiples servidores
async function sendMulticastMessage(message, expectedResponses) {
  return new Promise((resolve) => {
    const client = dgram.createSocket({ type: 'udp4', reuseAddr: true });
    let socketClosed = false; // Variable para evitar doble cierre del socket

    client.bind(localPort, () => {
      client.setBroadcast(true);
      client.setMulticastTTL(128);
      client.addMembership(multicastAddress);
    });

    const messageBuffer = Buffer.from(message);
    client.send(messageBuffer, multicastPort, multicastAddress, (err) => {
      if (err) {
        console.error('Error enviando multicast:', err);
        if (!socketClosed) {
          socketClosed = true;
          client.close();
        }
        resolve([]); // Resolver con array vacío en caso de error
      } else {
        console.log(`Mensaje multicast enviado: ${message}`);
      }
    });

    let responses = [];
    client.on('message', (msg, rinfo) => {
      console.log(`Confirmación recibida de ${rinfo.address}:${rinfo.port}: ${msg.toString()}`);
      if (!responses.includes(rinfo.address)) {
        responses.push(rinfo.address);
      }

      if (responses.length >= expectedResponses && !socketClosed) {
        socketClosed = true;
        client.close();
        resolve(responses);
      }
    });

    // Timeout para evitar esperas infinitas
    setTimeout(() => {
      if (!socketClosed) {
        console.log(`Respuestas recibidas antes del timeout: ${responses}`);
        socketClosed = true;
        client.close();
        resolve(responses);
      }
    }, 3000);
  });
}


const server = http.createServer(async (req, res) => {
  console.log(`Solicitud recibida: ${req.url}`);
  let servers_count = 1
  if 
  try {
    const clientIp = process.env.CONTAINER_IP || '0.0.0.0';
    console.log(`Enviando solicitud multicast con IP del cliente: ${clientIp}`);

    targetHosts = await sendMulticastMessage(clientIp, 3); // Esperamos respuestas de 2 servidores
    console.log('Servidores detectados:', targetHosts);

    if (targetHosts.length === 0) {
      console.error('No se encontraron servidores disponibles.');
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('No hay servidores disponibles.');
      return;
    }
  } catch (error) {
    console.error('Error en la comunicación multicast:', error);
  }

  // Crear una lista de promesas para cada servidor detectado
  const proxyRequests = targetHosts.map((host) => {
    return new Promise((resolve) => {
      const proxyReq = http.request(
        {
          hostname: host,
          port: targetPort,
          path: req.url,
          method: req.method,
          headers: req.headers,
        },
        (proxyRes) => {
          let data = '';

          proxyRes.on('data', (chunk) => {
            data += chunk;
          });

          proxyRes.on('end', () => {
            console.log(`Respuesta de ${host}:`, data);
            resolve({ server: host, data });
          });
        }
      );

      proxyReq.on('error', (err) => {
        console.error(`Error al reenviar la solicitud a ${host}:`, err);
        resolve(null);
      });

      req.pipe(proxyReq); // Enviar la solicitud original al backend
    });
  });

  // Esperar todas las respuestas
  const results = await Promise.all(proxyRequests);
  const validResponses = results.filter((result) => result !== null);

  if (validResponses.length > 0) {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify(validResponses));
  } else {
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Error al reenviar la solicitud a los servidores.');
  }
});

server.listen(8000, () => {
  console.log(`Proxy server escuchando en http://localhost:8000`);
});
