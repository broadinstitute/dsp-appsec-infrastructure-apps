# WARNING: Are you updating the template?
FROM node:latest as node
WORKDIR /app/website
COPY src/base/. .
COPY src/modules/CodeDx/Overview.md docs/SDARQ/Modules/CodeDx.md
COPY src/modules/CIS_Scanning/Overview.md docs/SDARQ/Modules/CIS_Scanning.md
COPY src/modules/DefectDojo/Overview.md docs/SDARQ/Modules/DefectDojo.md
COPY src/modules/Documentation/Overview.md docs/SDARQ/Modules/Documentation.md
COPY src/modules/Jira_Ticket_Assessment/Overview.md docs/SDARQ/Modules/Jira_Ticket_Assessment.md
COPY src/modules/New_Service_Requirements/Overview.md docs/SDARQ/Modules/New_Service_Requirements.md
COPY src/modules/SecExplorer/Overview.md docs/SDARQ/Modules/SecExplorer.md
COPY src/modules/Threat_Models/Overview.md docs/SDARQ/Modules/Threat_Models.md
COPY src/modules/Zap_Scanning/Overview.md docs/SDARQ/Modules/Zap_Scanning.md
RUN yarn install
RUN npm run build

FROM nginx:alpine
COPY --from=node /app/website/build/ /usr/share/nginx/html/