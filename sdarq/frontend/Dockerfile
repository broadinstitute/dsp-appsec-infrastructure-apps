FROM us.gcr.io/broad-dsp-gcr-public/base/nodejs:20-alpine AS node

WORKDIR /app

COPY package.* .
RUN npm install --legacy-peer-deps

COPY . .
RUN npm run lint
RUN npm run build -- --configuration production

FROM us.gcr.io/broad-dsp-gcr-public/base/nginx:mainline-alpine

COPY ./nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=node /app/dist /usr/share/nginx/html
