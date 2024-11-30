#!/bin/sh
sh /app/frontend.sh
echo "Iniciando servidor proxy..." &
node proxy.js &
echo "Servidor proxy iniciado."
