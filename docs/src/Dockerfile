FROM node:latest as node

WORKDIR /app/website

COPY ./website/package.json .

RUN yarn install

COPY ./docs /app/docs
COPY ./website .

RUN yarn build

FROM nginx:alpine
COPY --from=node /app/website/build/dsp-appsec-infrastructure-automation/ /usr/share/nginx/html/
