FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:20-alpine AS build
WORKDIR /app
ENV NODE_OPTIONS=--max-old-space-size=768
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build -- --sourcemap=false || npm run build
RUN set -eux; \
    mkdir -p /web; \
    if [ -d "/app/dist" ]; then cp -r /app/dist/* /web/; \
    elif [ -d "/app/build/client" ]; then cp -r /app/build/client/* /web/; \
    else ls -lah /app; exit 1; fi; \
    ls -lah /web

FROM nginx:1.25-alpine
COPY --from=build /web /usr/share/nginx/html
