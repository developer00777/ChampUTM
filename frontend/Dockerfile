FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json ./
RUN npm install

COPY . .

# VITE_API_URL must be set at build time (Railway injects it via env vars)
ARG VITE_API_URL
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

# Production stage — serve with nginx
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

# Railway sets $PORT dynamically — substitute it into nginx config at startup
CMD ["/bin/sh", "-c", "sed -i 's/listen 80/listen '\"$PORT\"'/g' /etc/nginx/conf.d/default.conf && nginx -g 'daemon off;'"]
