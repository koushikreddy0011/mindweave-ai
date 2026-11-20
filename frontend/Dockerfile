# Multi-stage build for MindWeave AI Frontend
FROM node:20-alpine AS builder
WORKDIR /app
# Copy dependency manifests
COPY package*.json ./
RUN npm ci
# Copy source code and build
COPY . .
RUN npm run build

# Stage 2: High-performance Nginx runtime
FROM nginx:alpine AS runner
# Remove default nginx welcome page
RUN rm -rf /usr/share/nginx/html/*
# Copy pre-compiled static files from builder
COPY --from=builder /app/dist /usr/share/nginx/html
# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget -q -O - http://127.0.0.1/ > /dev/null || exit 1
CMD ["nginx", "-g", "daemon off;"]
