FROM node:24-bookworm-slim
WORKDIR /app
COPY package.json ./
RUN npm install --omit=dev --no-audit --no-fund
COPY server.mjs ./server.mjs
COPY merkle.mjs ./merkle.mjs
COPY public ./public
USER node
EXPOSE 8080
CMD ["node", "server.mjs"]
