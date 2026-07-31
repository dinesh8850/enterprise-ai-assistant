# Dockerfile — multi-stage build for the React frontend.

# ---- Stage 1: "build" -- has Node.js, compiles our React app ----
FROM node:20-slim AS build

WORKDIR /app

# Same caching optimization as the backend: copy just the dependency
# manifest first, install, THEN copy the rest of the source code.
COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build
# npm run build produces a folder called "dist/" containing plain,
# optimized HTML/CSS/JS -- no React, no Node, no dev tooling needed
# to actually serve these files.

# ---- Stage 2: "serve" -- a tiny, production-grade web server ----
FROM nginx:alpine

# Copy ONLY the built static files from Stage 1 into this fresh,
# minimal image. Everything else from Stage 1 (Node, node_modules,
# source .jsx files) is discarded -- it never makes it into the
# final image at all.
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
