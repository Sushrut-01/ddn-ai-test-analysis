# Multi-stage Dockerfile for DDN AI Dashboard
# Supports both development and production modes

FROM node:18-alpine AS base

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (use legacy-peer-deps to resolve MUI version conflicts)
RUN npm install --legacy-peer-deps

# Copy application files
COPY . .

# ============================================================================
# Development Stage
# ============================================================================
FROM base AS development

# Expose Vite dev server port
EXPOSE 5173

# Run Vite dev server
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]

# ============================================================================
# Production Build Stage
# ============================================================================
FROM base AS builder

# Build the application
RUN npm run build

# ============================================================================
# Production Stage
# ============================================================================
FROM node:18-alpine AS production

WORKDIR /app

# Install serve for production
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 5173

# Serve the built application on port 5173
CMD ["serve", "-s", "dist", "-l", "5173"]
