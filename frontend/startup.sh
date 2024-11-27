#!/bin/sh
sh /app/frontend.sh
# echo "Instalando dependencias..."
# npm install
# echo "Dependencias instaladas."
echo "Iniciando servidor proxy..."
node proxy.js
echo "Servidor proxy iniciado."
echo "Iniciando servidor de desarrollo..."
npm run dev
echo "Servidor de desarrollo corriendo."
