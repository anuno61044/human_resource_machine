import http from 'http';
import httpProxy from 'http-proxy';

const targetHost = 'http://10.0.11.2'; // Backend IP
const targetPort = 8000;

const proxy = httpProxy.createProxyServer({});

const server = http.createServer((req, res) => {
  proxy.web(req, res, { target: `${targetHost}:${targetPort}` }, (err) => {
    
    console.log(`url = ${targetHost}:${targetPort}`);
    console.log(`request = ${req.url}`);


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