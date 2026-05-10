FROM node:20-alpine
WORKDIR /app

# Install deps first (better build cache)
COPY package.json package-lock.json* ./
RUN npm install --omit=dev

# App files
COPY server.js index.html ./

ENV PORT=8080
ENV NODE_ENV=production
# RAILWAY_VOLUME_MOUNT_PATH set automatically when a volume is attached;
# falls back to /tmp/test-geografia-data if missing (data won't persist across deploys).

EXPOSE 8080
CMD ["node", "server.js"]
