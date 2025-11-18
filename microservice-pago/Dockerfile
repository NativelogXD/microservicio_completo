# syntax=docker/dockerfile:1

FROM node:20-alpine AS builder
WORKDIR /usr/src/app
ENV NODE_ENV=development

# Install dependencies (including devDependencies for building)
COPY package*.json ./
RUN npm ci

# Copy configs and sources
COPY nest-cli.json ./
COPY tsconfig*.json ./
COPY src ./src

# Build the project
RUN npm run build

# --- Runtime image ---
FROM node:20-alpine AS runner
WORKDIR /usr/src/app
ENV NODE_ENV=production

# Install only production dependencies
COPY package*.json ./
RUN npm ci --omit=dev

# Copy built artifacts
COPY --from=builder /usr/src/app/dist ./dist

# Run as non-root user for security
USER node

# Expose NestJS port (matches PORT env)
EXPOSE 3000

# Start the service
ENV PORT=3000
CMD ["node", "dist/main.js"]