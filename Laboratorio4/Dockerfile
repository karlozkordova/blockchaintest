
FROM node:24-bookworm-slim

WORKDIR /app

# Crear proyecto Node.js
RUN npm init -y

# Habilitar ESM, requerido por Hardhat 3
RUN npm pkg set type="module"

# Instalar Hardhat
RUN npm install --save-dev hardhat@^3 ethers@^6 solc@^0.8.28


# Copiar configuración
COPY hardhat.config.ts ./

EXPOSE 8545

# Iniciar nodo Ethereum local
CMD ["npx", "hardhat", "node", "--network", "node", "--hostname", "0.0.0.0", "--port", "8545"]

