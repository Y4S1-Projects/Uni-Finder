# Frontend Dockerfile (React with Nginx)
# Multi-stage build for optimized production image

# Stage 1: Build the React application
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy application source
COPY . .

# Build arguments for API URLs (will be baked into the build)
ARG REACT_APP_BACKEND_URL
ARG REACT_APP_DEGREE_SERVICE_URL
ARG REACT_APP_BUDGET_SERVICE_URL
ARG REACT_APP_CAREER_SERVICE_URL
ARG REACT_APP_SCHOLARSHIP_SERVICE_URL

# Build the application
RUN npm run build

# Stage 2: Serve with Nginx
FROM nginx:1.27-alpine

# Copy custom Nginx configuration
COPY deploy/nginx/default.conf /etc/nginx/conf.d/default.conf

# Copy built assets from builder stage
COPY --from=builder /app/build /usr/share/nginx/html

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
