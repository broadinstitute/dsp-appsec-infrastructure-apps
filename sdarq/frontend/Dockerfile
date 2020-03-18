# stage 1
FROM node:latest AS node

WORKDIR /app

COPY package.* .
RUN npm install

COPY . .
RUN npm run lint
RUN npm run build -- --prod

# stage 2
FROM nginx:alpine
COPY --from=node /app/dist /usr/share/nginx/html/
