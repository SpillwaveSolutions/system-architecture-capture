FROM node:20-alpine AS build
WORKDIR /app
COPY package.json .
RUN npm install
COPY . .
RUN npm run build || true

FROM gcr.io/distroless/nodejs20
WORKDIR /app
COPY --from=build /app/dist ./dist
EXPOSE 8080
CMD ["dist/index.js"]
