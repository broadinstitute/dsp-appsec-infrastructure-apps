FROM node:lts AS node

WORKDIR /app

COPY package.* .
RUN npm install

COPY . .
RUN npm run lint
RUN npm run build -- --prod

FROM nginx:alpine
COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=node /app/dist /usr/share/nginx/html
