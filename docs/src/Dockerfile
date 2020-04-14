FROM node:latest as node

WORKDIR /app/website

COPY ./docs /app/docs
COPY ./website /app/website
RUN yarn install

CMD ["yarn", "build"]

FROM nginx:alpine
COPY --from=node /app/website/build/dsp-appsec-infrastructure-automation/ /usr/share/nginx/html/
RUN ls /usr/share/nginx/html/
