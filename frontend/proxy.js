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
  res.setHeader('Access-Control-Allow-Origin', '*'); // Permitir CORS
  res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');

  console.log(`Solicitud recibida: ${req.url}`);

  let servers_count = req.url === '/appSolution/solution/' ? 3 : 1;

  try {
    const clientIp = process.env.CONTAINER_IP || '0.0.0.0';
    console.log(`Enviando solicitud multicast con IP del cliente: ${clientIp}`);

    const targetHosts = await sendMulticastMessage(clientIp, servers_count);
    console.log('Servidores detectados:', targetHosts);

    if (targetHosts.length === 0) {
      console.error('No se encontraron servidores disponibles.');
      res.writeHead(500, { 'Content-Type': 'text/plain' });
      res.end('No hay servidores disponibles.');
      return;
    }

    let responded = false; // Variable para saber si ya respondimos

    targetHosts.forEach((host) => {
      const proxyReq = http.request(
        {
          hostname: host,
          port: targetPort,
          path: req.url,
          method: req.method,
          headers: req.headers,
        },
        (proxyRes) => {
          if (responded) return; // Si ya respondimos, ignoramos las demás respuestas
    
          responded = true; // Marcar que ya respondimos
          let responseData = '';
    
          proxyRes.on('data', (chunk) => {
            responseData += chunk; // Acumular los datos de la respuesta
          });
    
          proxyRes.on('end', () => {
            console.log(`✅ Respuesta desde ${host}: ${responseData}`); // Mostrar en consola
            res.writeHead(proxyRes.statusCode, proxyRes.headers); // Enviar headers
            res.end(responseData); // Enviar la respuesta al cliente
          });
        }
      );
    
      proxyReq.on('error', (err) => {
        console.error(`❌ Error al reenviar la solicitud a ${host}:`, err);
      });
    
      req.pipe(proxyReq); // Enviar la solicitud al backend
    });
    

    // Si después de 3 segundos no hay respuesta, enviar error
    setTimeout(() => {
      if (!responded) {
        console.log('⏳ Timeout: ningún servidor respondió.');
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('Error: Ningún servidor respondió.');
      }
    }, 60000);
  } catch (error) {
    console.error('❌ Error en la comunicación multicast:', error);
    res.writeHead(500, { 'Content-Type': 'text/plain' });
    res.end('Error en la comunicación multicast.');
  }
});

server.listen(8000, () => {
  console.log(`Proxy server escuchando en http://localhost:8000`);
});
