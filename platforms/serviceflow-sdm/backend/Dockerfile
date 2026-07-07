# Production multi-stage build (dev: use `npm run dev` on the host or override CMD in compose).
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runtime
WORKDIR /app
ENV NODE_ENV=production
COPY package*.json ./
RUN npm ci --omit=dev
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/public ./public
RUN chown -R node:node /app
EXPOSE 3000
USER node
CMD ["npm", "run", "start"]
