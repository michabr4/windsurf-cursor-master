Project Overview
Application Name: ServiceFlow SDM (Service Delivery Management Platform)
Customer Focus: MGM Resorts International (GES-West)
Purpose: Unified service delivery management platform with TAC integration, property-specific dashboards, and technology adoption tracking
Target Platforms: Web, Mobile (iOS/Android), Desktop
Key Integrations: MS Teams, WebEx, Cisco TAC, DNA Center, Smart Licensing
Development Philosophy
This guide is designed to be executed step-by-step. Each section builds upon the previous one. Complete each phase before moving to the next to ensure a solid foundation.
Table of Contents
Environment Setup
Project Initialization
Database Design & Implementation
Backend API Development
Frontend Development
Integration Layer
Testing & Quality Assurance
Deployment
Phase 1: Environment Setup
1.1 System Requirements Check
bash
Copy Code
# Check your system

echo
 
"Checking system requirements..."


# OS Check

uname
 -a

# Required: Linux (Ubuntu 22.04+), macOS (12+), or Windows with WSL2

# RAM: Minimum 16GB recommended

# Storage: 50GB free space

# Internet: Stable connection

1.2 Install Core Dependencies
For Ubuntu/Debian:
bash
Copy Code
# Update system

sudo
 apt update && 
sudo
 apt upgrade -y

# Install Node.js 20.x LTS

curl -fsSL https://deb.nodesource.com/setup_20.x | 
sudo
 -E bash -
sudo
 apt install -y nodejs

# Verify Node installation

node --version  
# Should show v20.x.x

npm --version   
# Should show 10.x.x


# Install PostgreSQL 15

sudo
 sh -c 
'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'

wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | 
sudo
 apt-key add -
sudo
 apt update
sudo
 apt install -y postgresql-15 postgresql-contrib-15

# Start PostgreSQL

sudo
 systemctl start postgresql
sudo
 systemctl 
enable
 postgresql

# Install Redis

sudo
 apt install -y redis-server
sudo
 systemctl start redis-server
sudo
 systemctl 
enable
 redis-server

# Install Docker

curl -fsSL https://get.docker.com -o get-docker.sh
sudo
 sh get-docker.sh
sudo
 usermod -aG docker 
$USER

newgrp docker

# Install Docker Compose

sudo
 curl -L 
"https://github.com/docker/compose/releases/latest/download/docker-compose-
$(uname -s)
-
$(uname -m)
"
 -o /usr/local/bin/docker-compose
sudo
 
chmod
 +x /usr/local/bin/docker-compose

# Install Git

sudo
 apt install -y git

# Install build essentials

sudo
 apt install -y build-essential python3 python3-pip
For macOS:
bash
Copy Code
# Install Homebrew if not installed

/bin/bash -c 
"
$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)
"


# Install Node.js

brew install node@20

# Install PostgreSQL

brew install postgresql@15
brew services start postgresql@15

# Install Redis

brew install redis
brew services start redis

# Install Docker Desktop

# Download from: https://www.docker.com/products/docker-desktop


# Install Git (usually pre-installed)

brew install git
1.3 Verify Installations
bash
Copy Code
# Verify all installations

echo
 
"Node version: 
$(node --version)
"

echo
 
"NPM version: 
$(npm --version)
"

echo
 
"PostgreSQL version: 
$(psql --version)
"

echo
 
"Redis version: 
$(redis-server --version)
"

echo
 
"Docker version: 
$(docker --version)
"

echo
 
"Docker Compose version: 
$(docker-compose --version)
"

echo
 
"Git version: 
$(git --version)
"

1.4 Configure PostgreSQL
bash
Copy Code
# Switch to postgres user

sudo
 -u postgres psql

# Inside PostgreSQL prompt, run:

CREATE USER serviceflow_admin WITH PASSWORD 
'your_secure_password_here'
;
CREATE DATABASE serviceflow_sdm OWNER serviceflow_admin;
GRANT ALL PRIVILEGES ON DATABASE serviceflow_sdm TO serviceflow_admin;
\q

# Test connection

psql -U serviceflow_admin -d serviceflow_sdm -h localhost
# Enter password when prompted

# Type \q to exit

1.5 Configure Redis
bash
Copy Code
# Edit Redis configuration (optional, for production)

sudo
 nano /etc/redis/redis.conf

# Uncomment and set:

# requirepass your_redis_password


# Restart Redis

sudo
 systemctl restart redis-server

# Test Redis

redis-cli ping
# Should return: PONG

Phase 2: Project Initialization
2.1 Create Project Structure
bash
Copy Code
# Create main project directory

mkdir
 -p ~/projects/serviceflow-sdm
cd
 ~/projects/serviceflow-sdm

# Initialize Git repository

git init
git config user.name 
"Your Name"

git config user.email 
"your.email@company.com"


# Create directory structure

mkdir
 -p {backend,frontend,mobile,shared,docs,scripts,tests,deployments}

# Create .gitignore

cat
 > .gitignore << 
'EOF'

# Dependencies

node_modules/
venv/
__pycache__/
*.pyc

# Environment files

.
env

.env.local
.
env
.*.
local

*.
env


# Build outputs

dist/
build/
*.
log

logs/

# IDE

.vscode/
.idea/
*.swp
*.swo
*.suo

# OS

.DS_Store
Thumbs.db
*.tmp

# Database

*.sqlite
*.db

# Secrets

secrets/
credentials/
*.pem
*.key
*.crt

# Testing

coverage/
.nyc_output/

# Misc

.cache/
temp/
EOF

# Create README

cat
 > README.md << 
'EOF'

# ServiceFlow SDM - Service Delivery Management Platform


## Overview

Unified platform 
for
 service delivery management with focus on MGM Resorts International.

## Features

- Property-specific dashboards
- Technology adoption tracking
- TAC integration and automation
- MS Teams and WebEx integration
- Real-
time
 monitoring and alerts

## Tech Stack

- Backend: Node.js, TypeScript, Express
- Frontend: React, TypeScript, Material-UI
- Database: PostgreSQL, Redis
- Mobile: React Native
- Integrations: MS Teams, WebEx, Cisco APIs

## Getting Started

See CLAUDE.md 
for
 detailed setup instructions.

## License

Proprietary - MGM Resorts International
EOF

# Initial commit

git add .
git commit -m 
"Initial project setup"

2.2 Backend Project Setup
bash
Copy Code
cd
 backend

# Initialize Node.js project

npm init -y

# Update package.json with project details

cat
 > package.json << 
'EOF'

{
  
"name"
: 
"serviceflow-sdm-backend"
,
  
"version"
: 
"1.0.0"
,
  
"description"
: 
"ServiceFlow SDM Backend API"
,
  
"main"
: 
"dist/server.js"
,
  
"scripts"
: {
    
"dev"
: 
"nodemon --exec ts-node src/server.ts"
,
    
"build"
: 
"tsc"
,
    
"start"
: 
"node dist/server.js"
,
    
"test"
: 
"jest --coverage"
,
    
"test:watch"
: 
"jest --watch"
,
    
"lint"
: 
"eslint . --ext .ts"
,
    
"lint:fix"
: 
"eslint . --ext .ts --fix"
,
    
"format"
: 
"prettier --write \"src/**/*.ts\""
,
    
"db:migrate"
: 
"ts-node scripts/migrate.ts"
,
    
"db:seed"
: 
"ts-node scripts/seed.ts"

  },
  
"keywords"
: [
"sdm"
, 
"service-delivery"
, 
"mgm"
, 
"cisco"
],
  
"author"
: 
"Your Name"
,
  
"license"
: 
"PROPRIETARY"
,
  
"engines"
: {
    
"node"
: 
">=20.0.0"
,
    
"npm"
: 
">=10.0.0"

  }
}
EOF

# Install production dependencies

npm install express@4.18.2 \
  cors@2.8.5 \
  helmet@7.1.0 \
  compression@1.7.4 \
  morgan@1.10.0 \
  dotenv@16.3.1 \
  pg@8.11.3 \
  redis@4.6.11 \
  ioredis@5.3.2 \
  axios@1.6.2 \
  jsonwebtoken@9.0.2 \
  bcrypt@5.1.1 \
  express-validator@7.0.1 \
  express-rate-limit@7.1.5 \
  socket.io@4.6.0 \
  winston@3.11.0 \
  node-cron@3.0.3 \
  bull@4.12.0 \
  uuid@9.0.1 \
  date-fns@2.30.0

# Install Microsoft Graph for Teams integration

npm install @microsoft/microsoft-graph-client@3.0.7 \
  @azure/msal-node@2.6.0

# Install development dependencies

npm install -D typescript@5.3.3 \
  ts-node@10.9.2 \
  nodemon@3.0.2 \
  @types/node@20.10.6 \
  @types/express@4.17.21 \
  @types/cors@2.8.17 \
  @types/jsonwebtoken@9.0.5 \
  @types/bcrypt@5.0.2 \
  @types/morgan@1.9.9 \
  @types/compression@1.7.5 \
  @types/uuid@9.0.7 \
  eslint@8.56.0 \
  @typescript-eslint/parser@6.17.0 \
  @typescript-eslint/eslint-plugin@6.17.0 \
  prettier@3.1.1 \
  jest@29.7.0 \
  ts-jest@29.1.1 \
  @types/jest@29.5.11 \
  supertest@6.3.3 \
  @types/supertest@6.0.2

# Create TypeScript configuration

cat
 > tsconfig.json << 
'EOF'

{
  
"compilerOptions"
: {
    
"target"
: 
"ES2022"
,
    
"module"
: 
"commonjs"
,
    
"lib"
: [
"ES2022"
],
    
"outDir"
: 
"./dist"
,
    
"rootDir"
: 
"./src"
,
    
"strict"
: 
true
,
    
"esModuleInterop"
: 
true
,
    
"skipLibCheck"
: 
true
,
    
"forceConsistentCasingInFileNames"
: 
true
,
    
"resolveJsonModule"
: 
true
,
    
"moduleResolution"
: 
"node"
,
    
"allowSyntheticDefaultImports"
: 
true
,
    
"experimentalDecorators"
: 
true
,
    
"emitDecoratorMetadata"
: 
true
,
    
"sourceMap"
: 
true
,
    
"declaration"
: 
true
,
    
"declarationMap"
: 
true
,
    
"noUnusedLocals"
: 
true
,
    
"noUnusedParameters"
: 
true
,
    
"noImplicitReturns"
: 
true
,
    
"noFallthroughCasesInSwitch"
: 
true

  },
  
"include"
: [
"src/**/*"
],
  
"exclude"
: [
"node_modules"
, 
"dist"
, 
"**/*.test.ts"
]
}
EOF

# Create ESLint configuration

cat
 > .eslintrc.json << 
'EOF'

{
  
"parser"
: 
"@typescript-eslint/parser"
,
  
"extends"
: [
    
"eslint:recommended"
,
    
"plugin:@typescript-eslint/recommended"

  ],
  
"parserOptions"
: {
    
"ecmaVersion"
: 2022,
    
"sourceType"
: 
"module"

  },
  
"rules"
: {
    
"@typescript-eslint/no-explicit-any"
: 
"warn"
,
    
"@typescript-eslint/explicit-function-return-type"
: 
"off"
,
    
"no-console"
: 
"warn"

  }
}
EOF

# Create Prettier configuration

cat
 > .prettierrc << 
'EOF'

{
  
"semi"
: 
true
,
  
"trailingComma"
: 
"es5"
,
  
"singleQuote"
: 
true
,
  
"printWidth"
: 100,
  
"tabWidth"
: 2,
  
"useTabs"
: 
false

}
EOF

# Create Jest configuration

cat
 > jest.config.js << 
'EOF'

module.exports = {
  preset: 
'ts-jest'
,
  testEnvironment: 
'node'
,
  roots: [
'<rootDir>/src'
, 
'<rootDir>/tests'
],
  testMatch: [
'**/__tests__/**/*.ts'
, 
'**/?(*.)+(spec|test).ts'
],
  collectCoverageFrom: [
    
'src/**/*.ts'
,
    
'!src/**/*.d.ts'
,
    
'!src/**/*.interface.ts'

  ],
  coverageDirectory: 
'coverage'
,
  coverageThreshold: {
    global: {
      branches: 70,
      
functions
: 70,
      lines: 70,
      statements: 70
    }
  }
};
EOF

# Create backend directory structure

mkdir
 -p src/{config,controllers,middleware,models,routes,services,utils,integrations,types}
mkdir
 -p src/integrations/{teams,webex,
tac
,dna-center,smart-licensing}
mkdir
 -p tests/{unit,integration,e2e}
mkdir
 -p logs
mkdir
 -p scripts

# Create environment template

cat
 > .env.example << 
'EOF'

# ============================================================================

# SERVER CONFIGURATION

# ============================================================================

NODE_ENV=development
PORT=3000
API_VERSION=v1
HOST=0.0.0.0

# ============================================================================

# DATABASE CONFIGURATION

# ============================================================================

DB_HOST=localhost
DB_PORT=5432
DB_NAME=serviceflow_sdm
DB_USER=serviceflow_admin
DB_PASSWORD=your_secure_password_here
DB_POOL_MIN=2
DB_POOL_MAX=10

# ============================================================================

# REDIS CONFIGURATION

# ============================================================================

REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

# ============================================================================

# JWT & SECURITY

# ============================================================================

JWT_SECRET=your_jwt_secret_key_minimum_32_characters_long
JWT_EXPIRE=24h
JWT_REFRESH_SECRET=your_refresh_token_secret_key_minimum_32_characters
JWT_REFRESH_EXPIRE=7d
BCRYPT_ROUNDS=12

# ============================================================================

# CORS CONFIGURATION

# ============================================================================

CORS_ORIGIN=http://localhost:3001,http://localhost:3000

# ============================================================================

# RATE LIMITING

# ============================================================================

RATE_LIMIT_WINDOW_MS=900000
RATE_LIMIT_MAX_REQUESTS=100

# ============================================================================

# MS TEAMS INTEGRATION

# ============================================================================

TEAMS_CLIENT_ID=your_azure_app_client_id
TEAMS_CLIENT_SECRET=your_azure_app_client_secret
TEAMS_TENANT_ID=your_azure_tenant_id
TEAMS_BOT_ID=your_teams_bot_id
TEAMS_BOT_PASSWORD=your_teams_bot_password
TEAMS_WEBHOOK_BASE_URL=https://your-app-domain.com

# ============================================================================

# WEBEX INTEGRATION

# ============================================================================

WEBEX_CLIENT_ID=your_webex_client_id
WEBEX_CLIENT_SECRET=your_webex_client_secret
WEBEX_BOT_TOKEN=your_webex_bot_access_token
WEBEX_WEBHOOK_SECRET=your_webhook_secret
WEBEX_REDIRECT_URI=https://your-app-domain.com/auth/webex/callback

# ============================================================================

# CISCO TAC INTEGRATION

# ============================================================================

TAC_API_KEY=your_tac_api_key
TAC_API_SECRET=your_tac_api_secret
TAC_BASE_URL=https://tools.cisco.com/tac/api/v2
TAC_CONTRACT_NUMBER=GES-W-2024-MGM

# ============================================================================

# CISCO DNA CENTER

# ============================================================================

DNA_CENTER_HOST=your-dnac-host.example.com
DNA_CENTER_USERNAME=your_dnac_username
DNA_CENTER_PASSWORD=your_dnac_password
DNA_CENTER_PORT=443

# ============================================================================

# CISCO SMART LICENSING

# ============================================================================

SMART_LICENSING_CLIENT_ID=your_smart_licensing_client_id
SMART_LICENSING_CLIENT_SECRET=your_smart_licensing_client_secret
SMART_LICENSING_TOKEN_URL=https://cloudsso.cisco.com/as/token.oauth2
SMART_LICENSING_API_URL=https://swapi.cisco.com/services/api/smart-accounts-and-licensing

# ============================================================================

# EMAIL CONFIGURATION

# ============================================================================

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_SECURE=
false

SMTP_USER=your_email@company.com
SMTP_PASSWORD=your_email_app_password
EMAIL_FROM=noreply@serviceflow-sdm.com

# ============================================================================

# AWS CONFIGURATION (for production deployment)

# ============================================================================

AWS_REGION=us-west-2
AWS_ACCESS_KEY_ID=your_aws_access_key
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=serviceflow-sdm-uploads

# ============================================================================

# LOGGING

# ============================================================================

LOG_LEVEL=info
LOG_FILE=logs/app.log
LOG_MAX_SIZE=10m
LOG_MAX_FILES=7

# ============================================================================

# WEBSOCKET

# ============================================================================

SOCKET_IO_PATH=/socket.io
SOCKET_IO_CORS=http://localhost:3001

# ============================================================================

# MONITORING & METRICS

# ============================================================================

ENABLE_METRICS=
true

METRICS_PORT=9090

# ============================================================================

# FEATURE FLAGS

# ============================================================================

ENABLE_TAC_AUTO_CREATE=
true

ENABLE_TEAMS_INTEGRATION=
true

ENABLE_WEBEX_INTEGRATION=
true

ENABLE_EMAIL_NOTIFICATIONS=
true

EOF

# Copy to actual .env file

cp
 .env.example .
env

echo
 
"⚠️  IMPORTANT: Edit backend/.env with your actual credentials!"

2.3 Frontend Project Setup
bash
Copy Code
cd
 ../frontend

# Create React app with TypeScript

npx create-react-app . --template typescript


# Install core dependencies

npm install react-router-dom@6.21.1 \
  axios@1.6.2 \
  @reduxjs/toolkit@2.0.1 \
  react-redux@9.0.4

# Install UI framework (Material-UI)

npm install @mui/material@5.15.2 \
  @mui/icons-material@5.15.2 \
  @emotion/react@11.11.3 \
  @emotion/styled@11.11.0

# Install charting libraries

npm install recharts@2.10.3 \
  chart.js@4.4.1 \
  react-chartjs-2@5.2.0

# Install form handling

npm install react-hook-form@7.49.2 \
  yup@1.3.3 \
  @hookform/resolvers@3.3.3

# Install utilities

npm install date-fns@2.30.0 \
  lodash@4.17.21 \
  socket.io-client@4.6.0 \
  react-toastify@9.1.3

# Install dev dependencies

npm install -D @types/react-router-dom@5.3.3 \
  @types/lodash@4.14.202

# Update package.json scripts

cat
 > package.json << 
'EOF'

{
  
"name"
: 
"serviceflow-sdm-frontend"
,
  
"version"
: 
"1.0.0"
,
  
"private"
: 
true
,
  
"dependencies"
: {
    
"@emotion/react"
: 
"^11.11.3"
,
    
"@emotion/styled"
: 
"^11.11.0"
,
    
"@hookform/resolvers"
: 
"^3.3.3"
,
    
"@mui/icons-material"
: 
"^5.15.2"
,
    
"@mui/material"
: 
"^5.15.2"
,
    
"@reduxjs/toolkit"
: 
"^2.0.1"
,
    
"axios"
: 
"^1.6.2"
,
    
"chart.js"
: 
"^4.4.1"
,
    
"date-fns"
: 
"^2.30.0"
,
    
"lodash"
: 
"^4.17.21"
,
    
"react"
: 
"^18.2.0"
,
    
"react-chartjs-2"
: 
"^5.2.0"
,
    
"react-dom"
: 
"^18.2.0"
,
    
"react-hook-form"
: 
"^7.49.2"
,
    
"react-redux"
: 
"^9.0.4"
,
    
"react-router-dom"
: 
"^6.21.1"
,
    
"react-scripts"
: 
"5.0.1"
,
    
"react-toastify"
: 
"^9.1.3"
,
    
"recharts"
: 
"^2.10.3"
,
    
"socket.io-client"
: 
"^4.6.0"
,
    
"typescript"
: 
"^4.9.5"
,
    
"yup"
: 
"^1.3.3"

  },
  
"devDependencies"
: {
    
"@types/jest"
: 
"^27.5.2"
,
    
"@types/lodash"
: 
"^4.14.202"
,
    
"@types/node"
: 
"^16.18.68"
,
    
"@types/react"
: 
"^18.2.45"
,
    
"@types/react-dom"
: 
"^18.2.18"
,
    
"@types/react-router-dom"
: 
"^5.3.3"

  },
  
"scripts"
: {
    
"start"
: 
"react-scripts start"
,
    
"build"
: 
"react-scripts build"
,
    
"test"
: 
"react-scripts test"
,
    
"eject"
: 
"react-scripts eject"
,
    
"lint"
: 
"eslint src --ext .ts,.tsx"
,
    
"format"
: 
"prettier --write \"src/**/*.{ts,tsx}\""

  },
  
"eslintConfig"
: {
    
"extends"
: [
      
"react-app"
,
      
"react-app/jest"

    ]
  },
  
"browserslist"
: {
    
"production"
: [
      
">0.2%"
,
      
"not dead"
,
      
"not op_mini all"

    ],
    
"development"
: [
      
"last 1 chrome version"
,
      
"last 1 firefox version"
,
      
"last 1 safari version"

    ]
  },
  
"proxy"
: 
"http://localhost:3000"

}
EOF

# Create frontend directory structure

mkdir
 -p src/{components,pages,services,store,utils,hooks,types,assets,styles}
mkdir
 -p src/components/{common,dashboard,properties,technologies,incidents,reports,layout}
mkdir
 -p src/pages/{Dashboard,Properties,Technologies,Incidents,TAC,Reports,Settings,Auth}
mkdir
 -p src/services/{api,integrations}
mkdir
 -p src/store/{slices,middleware}

# Create environment file

cat
 > .
env
 << 
'EOF'

REACT_APP_API_BASE_URL=http://localhost:3000/api/v1
REACT_APP_SOCKET_URL=http://localhost:3000
REACT_APP_ENVIRONMENT=development
REACT_APP_VERSION=1.0.0
EOF

cat
 > .env.production << 
'EOF'

REACT_APP_API_BASE_URL=https://api.serviceflow-sdm.com/api/v1
REACT_APP_SOCKET_URL=https://api.serviceflow-sdm.com
REACT_APP_ENVIRONMENT=production
REACT_APP_VERSION=1.0.0
EOF
2.4 Docker Configuration
bash
Copy Code
cd
 ~/projects/serviceflow-sdm

# Create Docker Compose configuration

cat
 > docker-compose.yml << 
'EOF'

version: 
'3.8'


services:
  
# PostgreSQL Database

  postgres:
    image: postgres:15-alpine
    container_name: serviceflow-postgres
    environment:
      POSTGRES_DB: serviceflow_sdm
      POSTGRES_USER: serviceflow_admin
      POSTGRES_PASSWORD: postgres_dev_password
      PGDATA: /var/lib/postgresql/data/pgdata
    ports:
      - 
"5432:5432"

    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/db:/docker-entrypoint-initdb.d
    networks:
      - serviceflow-network
    healthcheck:
      
test
: [
"CMD-SHELL"
, 
"pg_isready -U serviceflow_admin -d serviceflow_sdm"
]
      interval: 10s
      
timeout
: 5s
      retries: 5

  
# Redis Cache

  redis:
    image: redis:7-alpine
    container_name: serviceflow-redis
    
command
: redis-server --appendonly 
yes
 --requirepass redis_dev_password
    ports:
      - 
"6379:6379"

    volumes:
      - redis_data:/data
    networks:
      - serviceflow-network
    healthcheck:
      
test
: [
"CMD"
, 
"redis-cli"
, 
"ping"
]
      interval: 10s
      
timeout
: 3s
      retries: 5

  
# Backend API

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    container_name: serviceflow-backend
    environment:
      NODE_ENV: development
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: serviceflow_sdm
      DB_USER: serviceflow_admin
      DB_PASSWORD: postgres_dev_password
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: redis_dev_password
      PORT: 3000
    ports:
      - 
"3000:3000"

      - 
"9229:9229"

    volumes:
      - ./backend:/app
      - /app/node_modules
      - ./backend/logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    networks:
      - serviceflow-network
    
command
: npm run dev

  
# Frontend Application

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    container_name: serviceflow-frontend
    environment:
      REACT_APP_API_BASE_URL: http://localhost:3000/api/v1
      REACT_APP_SOCKET_URL: http://localhost:3000
      WDS_SOCKET_PORT: 0
    ports:
      - 
"3001:3000"

    volumes:
      - ./frontend:/app
      - /app/node_modules
    depends_on:
      - backend
    networks:
      - serviceflow-network
    stdin_open: 
true

    
tty
: 
true

    
command
: npm start

  
# pgAdmin (Database Management UI)

  pgadmin:
    image: dpage/pgadmin4:latest
    container_name: serviceflow-pgadmin
    environment:
      PGADMIN_DEFAULT_EMAIL: admin@serviceflow.com
      PGADMIN_DEFAULT_PASSWORD: admin
      PGADMIN_LISTEN_PORT: 80
    ports:
      - 
"5050:80"

    volumes:
      - pgadmin_data:/var/lib/pgadmin
    depends_on:
      - postgres
    networks:
      - serviceflow-network

volumes:
  postgres_data:
    driver: 
local

  redis_data:
    driver: 
local

  pgadmin_data:
    driver: 
local


networks:
  serviceflow-network:
    driver: bridge
EOF

# Create backend Dockerfile for development

cat
 > backend/Dockerfile.dev << 
'EOF'

FROM node:20-alpine

# Set working directory

WORKDIR /app

# Install dependencies

COPY package*.json ./
RUN npm ci

# Copy source code

COPY . .

# Expose ports (3000 for API, 9229 for debugging)

EXPOSE 3000 9229

# Start in development mode

CMD [
"npm"
, 
"run"
, 
"dev"
]
EOF

# Create frontend Dockerfile for development

cat
 > frontend/Dockerfile.dev << 
'EOF'

FROM node:20-alpine

# Set working directory

WORKDIR /app

# Install dependencies

COPY package*.json ./
RUN npm ci

# Copy source code

COPY . .

# Expose port

EXPOSE 3000

# Start development server

CMD [
"npm"
, 
"start"
]
EOF

# Create production Dockerfiles

cat
 > backend/Dockerfile << 
'EOF'

FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files

COPY package*.json ./
RUN npm ci --only=production

# Copy source

COPY . .

# Build TypeScript

RUN npm run build

# Production image

FROM node:20-alpine

WORKDIR /app

# Copy built assets and dependencies

COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/package*.json ./

# Create non-root user

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Change ownership

RUN 
chown
 -R nodejs:nodejs /app

# Switch to non-root user

USER nodejs

EXPOSE 3000

# Health check

HEALTHCHECK --interval=30s --
timeout
=3s --start-period=40s \
  CMD node -e 
"require('http').get('http://localhost:3000/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"


CMD [
"node"
, 
"dist/server.js"
]
EOF

cat
 > frontend/Dockerfile << 
'EOF'

FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files

COPY package*.json ./
RUN npm ci

# Copy source

COPY . .

# Build for production

RUN npm run build

# Production image with nginx

FROM nginx:alpine

# Copy built assets

COPY --from=builder /app/build /usr/share/nginx/html

# Copy nginx configuration

COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD [
"nginx"
, 
"-g"
, 
"daemon off;"
]
EOF

# Create nginx configuration for frontend

cat
 > frontend/nginx.conf << 
'EOF'

server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    location / {
        try_files 
$uri
 
$uri
/ /index.html;
    }

    location /api {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade 
$http_upgrade
;
        proxy_set_header Connection 
'upgrade'
;
        proxy_set_header Host 
$host
;
        proxy_cache_bypass 
$http_upgrade
;
    }

    location /socket.io {
        proxy_pass http://backend:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade 
$http_upgrade
;
        proxy_set_header Connection 
"upgrade"
;
        proxy_set_header Host 
$host
;
        proxy_cache_bypass 
$http_upgrade
;
    }
}
EOF

# Create docker ignore files

cat
 > backend/.dockerignore << 
'EOF'

node_modules
npm-debug.log
.
env

.env.local
dist
coverage
.git
.gitignore
README.md
EOF

cat
 > frontend/.dockerignore << 
'EOF'

node_modules
npm-debug.log
build
.env.local
coverage
.git
.gitignore
README.md
EOF
Phase 3: Database Design & Implementation
3.1 Create Database Schema
bash
Copy Code
cd
 ~/projects/serviceflow-sdm/scripts
mkdir
 -p db

# Create comprehensive database schema

cat
 > db/01_schema.sql << 
'EOF'

-- ============================================================================
-- ServiceFlow SDM Database Schema
-- Version: 1.0.0
-- Description: Complete database schema 
for
 MGM Resorts service delivery
-- ============================================================================

-- Create extensions
CREATE EXTENSION IF NOT EXISTS 
"uuid-ossp"
;
CREATE EXTENSION IF NOT EXISTS 
"pg_trgm"
;
CREATE EXTENSION IF NOT EXISTS 
"pgcrypto"
;

-- Create schemas
CREATE SCHEMA IF NOT EXISTS mgm;
CREATE SCHEMA IF NOT EXISTS cisco;
CREATE SCHEMA IF NOT EXISTS audit;

-- Set default search path
SET search_path TO mgm, public;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Users & Authentication
CREATE TABLE mgm.users (
    user_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    full_name VARCHAR(255) GENERATED ALWAYS AS (first_name || 
' '
 || last_name) STORED,
    role VARCHAR(50) NOT NULL CHECK (role IN (
'admin'
, 
'sdm'
, 
'tam'
, 
'csm'
, 
'engineer'
, 
'manager'
, 
'viewer'
)),
    phone VARCHAR(20),
    mobile VARCHAR(20),
    timezone VARCHAR(50) DEFAULT 
'America/Los_Angeles'
,
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    last_login TIMESTAMP WITH TIME ZONE,
    login_count INTEGER DEFAULT 0,
    failed_login_attempts INTEGER DEFAULT 0,
    password_changed_at TIMESTAMP WITH TIME ZONE,
    profile_picture_url TEXT,
    preferences JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

COMMENT ON TABLE mgm.users IS 
'System users including SDMs, TAMs, engineers, and MGM staff'
;

-- Properties (MGM Resorts locations)
CREATE TABLE mgm.properties (
    property_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_code VARCHAR(20) UNIQUE NOT NULL,
    property_name VARCHAR(255) NOT NULL,
    address VARCHAR(500),
    city VARCHAR(100),
    state VARCHAR(50),
    zip_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 
'US'
,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    property_type VARCHAR(50) CHECK (property_type IN (
'hotel'
, 
'casino'
, 
'resort'
, 
'venue'
)),
    room_count INTEGER,
    employee_count INTEGER,
    square_footage INTEGER,
    it_manager_id UUID REFERENCES mgm.users(user_id),
    contact_phone VARCHAR(20),
    contact_email VARCHAR(255),
    emergency_contact VARCHAR(255),
    operating_hours JSONB,
    timezone VARCHAR(50) DEFAULT 
'America/Los_Angeles'
,
    is_active BOOLEAN DEFAULT TRUE,
    opened_date DATE,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE mgm.properties IS 
'MGM Resort properties (hotels, casinos, venues)'
;

-- Devices (Network infrastructure)
CREATE TABLE mgm.devices (
    device_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES mgm.properties(property_id) ON DELETE CASCADE,
    hostname VARCHAR(255) NOT NULL,
    ip_address INET,
    ipv6_address INET,
    mac_address VARCHAR(17),
    serial_number VARCHAR(100) UNIQUE,
    device_type VARCHAR(100) NOT NULL,
    device_category VARCHAR(50),
    model VARCHAR(100),
    vendor VARCHAR(50) DEFAULT 
'Cisco'
,
    software_version VARCHAR(100),
    hardware_revision VARCHAR(50),
    location VARCHAR(500),
    rack_location VARCHAR(100),
    floor VARCHAR(20),
    building VARCHAR(100),
    role VARCHAR(100),
    status VARCHAR(50) DEFAULT 
'active'
 CHECK (status IN (
'active'
, 
'inactive'
, 
'maintenance'
, 
'decommissioned'
, 
'failed'
)),
    health_score INTEGER CHECK (health_score BETWEEN 0 AND 100),
    cpu_utilization INTEGER,
    memory_utilization INTEGER,
    
uptime
 BIGINT,
    last_seen TIMESTAMP WITH TIME ZONE,
    last_reboot TIMESTAMP WITH TIME ZONE,
    dna_managed BOOLEAN DEFAULT FALSE,
    dna_device_id VARCHAR(255),
    smart_license_status VARCHAR(50),
    license_level VARCHAR(100),
    contract_number VARCHAR(100),
    contract_type VARCHAR(100),
    contract_start_date DATE,
    contract_expiry DATE,
    warranty_expiry DATE,
    eol_date DATE,
    eos_date DATE,
    purchase_date DATE,
    purchase_cost DECIMAL(15, 2),
    tags TEXT[],
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE mgm.devices IS 
'Network devices and infrastructure equipment'
;

-- Create indexes 
for
 devices
CREATE INDEX idx_devices_property ON mgm.devices(property_id);
CREATE INDEX idx_devices_serial ON mgm.devices(serial_number);
CREATE INDEX idx_devices_hostname ON mgm.devices(hostname);
CREATE INDEX idx_devices_type ON mgm.devices(device_type);
CREATE INDEX idx_devices_status ON mgm.devices(status);
CREATE INDEX idx_devices_ip ON mgm.devices(ip_address);
CREATE INDEX idx_devices_dna ON mgm.devices(dna_device_id);

-- Incidents
CREATE TABLE mgm.incidents (
    incident_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_number VARCHAR(50) UNIQUE NOT NULL,
    property_id UUID REFERENCES mgm.properties(property_id),
    device_id UUID REFERENCES mgm.devices(device_id),
    parent_incident_id UUID REFERENCES mgm.incidents(incident_id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    priority VARCHAR(10) NOT NULL CHECK (priority IN (
'P1'
, 
'P2'
, 
'P3'
, 
'P4'
)),
    status VARCHAR(50) NOT NULL DEFAULT 
'open'
 CHECK (status IN (
'open'
, 
'acknowledged'
, 
'investigating'
, 
'in-progress'
, 
'pending'
, 
'resolved'
, 
'closed'
, 
'cancelled'
)),
    category VARCHAR(100),
    subcategory VARCHAR(100),
    impact VARCHAR(50) CHECK (impact IN (
'critical'
, 
'high'
, 
'medium'
, 
'low'
)),
    urgency VARCHAR(50) CHECK (urgency IN (
'critical'
, 
'high'
, 
'medium'
, 
'low'
)),
    affected_services TEXT[],
    affected_users_count INTEGER DEFAULT 0,
    revenue_impact DECIMAL(15, 2),
    business_impact TEXT,
    reported_by UUID REFERENCES mgm.users(user_id),
    reported_via VARCHAR(50),
    assigned_to UUID REFERENCES mgm.users(user_id),
    assigned_team VARCHAR(100),
    tac_case_number VARCHAR(100),
    tac_case_id UUID,
    tac_severity VARCHAR(10),
    root_cause TEXT,
    resolution TEXT,
    workaround TEXT,
    resolution_time INTERVAL,
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    first_response_at TIMESTAMP WITH TIME ZONE,
    investigating_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    sla_target TIMESTAMP WITH TIME ZONE,
    sla_breach BOOLEAN DEFAULT FALSE,
    sla_breach_reason TEXT,
    war_room_url TEXT,
    teams_channel_id VARCHAR(255),
    webex_space_id VARCHAR(255),
    attachments JSONB DEFAULT 
'[]'
,
    tags TEXT[],
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE mgm.incidents IS 
'Service incidents and problems'
;

-- Create indexes 
for
 incidents
CREATE INDEX idx_incidents_number ON mgm.incidents(incident_number);
CREATE INDEX idx_incidents_property ON mgm.incidents(property_id);
CREATE INDEX idx_incidents_device ON mgm.incidents(device_id);
CREATE INDEX idx_incidents_status ON mgm.incidents(status);
CREATE INDEX idx_incidents_priority ON mgm.incidents(priority);
CREATE INDEX idx_incidents_opened ON mgm.incidents(opened_at DESC);
CREATE INDEX idx_incidents_tac_case ON mgm.incidents(tac_case_number);
CREATE INDEX idx_incidents_assigned ON mgm.incidents(assigned_to);

-- Incident Updates
CREATE TABLE mgm.incident_updates (
    update_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    incident_id UUID REFERENCES mgm.incidents(incident_id) ON DELETE CASCADE,
    user_id UUID REFERENCES mgm.users(user_id),
    update_type VARCHAR(50) CHECK (update_type IN (
'note'
, 
'status_change'
, 
'assignment'
, 
'escalation'
, 
'resolution'
, 
'closure'
)),
    content TEXT NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    old_assignee UUID,
    new_assignee UUID,
    is_customer_visible BOOLEAN DEFAULT FALSE,
    attachments JSONB DEFAULT 
'[]'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE mgm.incident_updates IS 
'Incident history and updates'
;

-- TAC Cases
CREATE TABLE cisco.tac_cases (
    tac_case_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    case_number VARCHAR(100) UNIQUE NOT NULL,
    incident_id UUID REFERENCES mgm.incidents(incident_id),
    property_id UUID REFERENCES mgm.properties(property_id),
    device_id UUID REFERENCES mgm.devices(device_id),
    severity VARCHAR(10) NOT NULL CHECK (severity IN (
'1'
, 
'2'
, 
'3'
, 
'4'
)),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    product_family VARCHAR(100),
    product_series VARCHAR(100),
    problem_type VARCHAR(100),
    problem_code VARCHAR(100),
    technology VARCHAR(100),
    tac_engineer_name VARCHAR(255),
    tac_engineer_email VARCHAR(255),
    tac_engineer_phone VARCHAR(20),
    tac_engineer_cco_id VARCHAR(100),
    status VARCHAR(50) NOT NULL CHECK (status IN (
'open'
, 
'in-progress'
, 
'pending-customer'
, 
'pending-cisco'
, 
'resolved'
, 
'closed'
)),
    sub_status VARCHAR(100),
    created_by UUID REFERENCES mgm.users(user_id),
    contract_number VARCHAR(100),
    opened_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    first_response_at TIMESTAMP WITH TIME ZONE,
    last_update_at TIMESTAMP WITH TIME ZONE,
    resolved_at TIMESTAMP WITH TIME ZONE,
    closed_at TIMESTAMP WITH TIME ZONE,
    resolution TEXT,
    resolution_code VARCHAR(100),
    closure_notes TEXT,
    war_room_url TEXT,
    webex_space_id VARCHAR(255),
    attachments JSONB DEFAULT 
'[]'
,
    related_bug_ids TEXT[],
    escalation_level INTEGER DEFAULT 0,
    escalation_reason TEXT,
    customer_satisfaction INTEGER CHECK (customer_satisfaction BETWEEN 1 AND 5),
    feedback TEXT,
    auto_created BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE cisco.tac_cases IS 
'Cisco TAC support cases'
;

-- Create indexes 
for
 TAC cases
CREATE INDEX idx_tac_cases_number ON cisco.tac_cases(case_number);
CREATE INDEX idx_tac_cases_incident ON cisco.tac_cases(incident_id);
CREATE INDEX idx_tac_cases_severity ON cisco.tac_cases(severity);
CREATE INDEX idx_tac_cases_status ON cisco.tac_cases(status);
CREATE INDEX idx_tac_cases_opened ON cisco.tac_cases(opened_at DESC);

-- TAC Case Updates
CREATE TABLE cisco.tac_case_updates (
    update_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    tac_case_id UUID REFERENCES cisco.tac_cases(tac_case_id) ON DELETE CASCADE,
    update_type VARCHAR(50) CHECK (update_type IN (
'note'
, 
'status_update'
, 
'engineer_note'
, 
'customer_update'
, 
'resolution'
, 
'escalation'
)),
    content TEXT NOT NULL,
    author VARCHAR(255),
    author_type VARCHAR(50) CHECK (author_type IN (
'customer'
, 
'tac'
, 
'system'
)),
    attachments JSONB DEFAULT 
'[]'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Technologies
CREATE TABLE cisco.technologies (
    technology_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    technology_name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL CHECK (category IN (
'Network Infrastructure'
, 
'Security'
, 
'Wireless'
, 
'Collaboration'
, 
'Data Center'
, 
'Observability'
, 
'Cloud'
)),
    subcategory VARCHAR(100),
    vendor VARCHAR(100) DEFAULT 
'Cisco'
,
    description TEXT,
    product_family VARCHAR(100),
    documentation_url TEXT,
    contract_included BOOLEAN DEFAULT TRUE,
    deployment_phase VARCHAR(50) CHECK (deployment_phase IN (
'planning'
, 
'design'
, 
'pilot'
, 
'deployment'
, 
'production'
, 
'complete'
)),
    target_adoption_percent INTEGER CHECK (target_adoption_percent BETWEEN 0 AND 100),
    current_adoption_percent INTEGER CHECK (current_adoption_percent BETWEEN 0 AND 100) DEFAULT 0,
    status VARCHAR(50) DEFAULT 
'planned'
 CHECK (status IN (
'planned'
, 
'in-progress'
, 
'deployed'
, 
'decommissioned'
)),
    planned_start_date DATE,
    planned_completion_date DATE,
    actual_start_date DATE,
    actual_completion_date DATE,
    project_manager UUID REFERENCES mgm.users(user_id),
    technical_lead UUID REFERENCES mgm.users(user_id),
    business_value TEXT,
    success_criteria TEXT,
    risks TEXT,
    dependencies TEXT[],
    budget_allocated DECIMAL(15, 2),
    budget_spent DECIMAL(15, 2),
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE cisco.technologies IS 
'Technology portfolio and adoption tracking'
;

-- Property Technology Adoption
CREATE TABLE mgm.property_technology_adoption (
    adoption_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES mgm.properties(property_id) ON DELETE CASCADE,
    technology_id UUID REFERENCES cisco.technologies(technology_id) ON DELETE CASCADE,
    adoption_status VARCHAR(50) NOT NULL CHECK (adoption_status IN (
'not-started'
, 
'planning'
, 
'in-progress'
, 
'deployed'
, 
'complete'
, 
'on-hold'
, 
'cancelled'
)),
    adoption_percent INTEGER CHECK (adoption_percent BETWEEN 0 AND 100) DEFAULT 0,
    devices_deployed INTEGER DEFAULT 0,
    devices_planned INTEGER DEFAULT 0,
    users_active INTEGER DEFAULT 0,
    users_planned INTEGER DEFAULT 0,
    deployment_phase VARCHAR(50),
    phase_start_date DATE,
    phase_completion_date DATE,
    actual_completion_date DATE,
    health_status VARCHAR(50) CHECK (health_status IN (
'healthy'
, 
'warning'
, 
'critical'
, 
'unknown'
)),
    health_score INTEGER CHECK (health_score BETWEEN 0 AND 100),
    blockers TEXT,
    notes TEXT,
    local_lead UUID REFERENCES mgm.users(user_id),
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id, technology_id)
);

COMMENT ON TABLE mgm.property_technology_adoption IS 
'Technology adoption tracking per property'
;

-- Technology Adoption History
CREATE TABLE mgm.adoption_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    adoption_id UUID REFERENCES mgm.property_technology_adoption(adoption_id) ON DELETE CASCADE,
    adoption_percent INTEGER,
    health_score INTEGER,
    devices_deployed INTEGER,
    users_active INTEGER,
    notes TEXT,
    recorded_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Licenses
CREATE TABLE cisco.licenses (
    license_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_type VARCHAR(100) NOT NULL,
    product_family VARCHAR(100) NOT NULL,
    product_name VARCHAR(255),
    sku VARCHAR(100),
    quantity_purchased INTEGER NOT NULL,
    quantity_consumed INTEGER DEFAULT 0,
    quantity_reserved INTEGER DEFAULT 0,
    quantity_available INTEGER GENERATED ALWAYS AS (quantity_purchased - quantity_consumed - quantity_reserved) STORED,
    utilization_percent INTEGER GENERATED ALWAYS AS (
        CASE 
            WHEN quantity_purchased > 0 THEN ((quantity_consumed + quantity_reserved) * 
100
 / quantity_purchased)
            ELSE 
0

        END
    ) STORED,
    license_model VARCHAR(
50
) CHECK (license_model IN ('perpetual', 'subscription', 'term', 'consumption')),
    purchase_date DATE,
    start_date DATE,
    expiry_date DATE,
    renewal_date DATE,
    renewal_window_days INTEGER DEFAULT 90,
    unit_cost DECIMAL(15, 2),
    annual_cost DECIMAL(15, 2),
    total_cost DECIMAL(15, 2),
    currency VARCHAR(10) DEFAULT 
'USD'
,
    contract_number VARCHAR(100),
    po_number VARCHAR(100),
    smart_account VARCHAR(255),
    virtual_account VARCHAR(255),
    status VARCHAR(50) DEFAULT 
'active'
 CHECK (status IN (
'active'
, 
'expiring'
, 
'expired'
, 
'cancelled'
, 
'pending'
)),
    compliance_status VARCHAR(50) CHECK (compliance_status IN (
'compliant'
, 
'non-compliant'
, 
'unknown'
)),
    auto_renewal BOOLEAN DEFAULT FALSE,
    alert_threshold INTEGER DEFAULT 80,
    vendor VARCHAR(100) DEFAULT 
'Cisco'
,
    vendor_contact VARCHAR(255),
    internal_owner UUID REFERENCES mgm.users(user_id),
    notes TEXT,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE cisco.licenses IS 
'Software licenses and subscriptions'
;

-- License Usage by Property
CREATE TABLE mgm.property_license_usage (
    usage_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_id UUID REFERENCES cisco.licenses(license_id) ON DELETE CASCADE,
    property_id UUID REFERENCES mgm.properties(property_id) ON DELETE CASCADE,
    quantity_used INTEGER DEFAULT 0,
    device_count INTEGER DEFAULT 0,
    user_count INTEGER DEFAULT 0,
    devices JSONB DEFAULT 
'[]'
,
    
users
 JSONB DEFAULT 
'[]'
,
    last_sync TIMESTAMP WITH TIME ZONE,
    sync_source VARCHAR(50),
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(license_id, property_id)
);

-- License History
CREATE TABLE cisco.license_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    license_id UUID REFERENCES cisco.licenses(license_id) ON DELETE CASCADE,
    event_type VARCHAR(50) CHECK (event_type IN (
'purchased'
, 
'renewed'
, 
'consumed'
, 
'released'
, 
'expired'
, 
'modified'
)),
    quantity_change INTEGER,
    old_quantity INTEGER,
    new_quantity INTEGER,
    old_expiry_date DATE,
    new_expiry_date DATE,
    reason TEXT,
    performed_by UUID REFERENCES mgm.users(user_id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- SLA Metrics
CREATE TABLE mgm.sla_metrics (
    metric_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES mgm.properties(property_id) ON DELETE CASCADE,
    metric_date DATE NOT NULL,
    metric_type VARCHAR(50) DEFAULT 
'daily'
 CHECK (metric_type IN (
'daily'
, 
'weekly'
, 
'monthly'
, 
'quarterly'
, 
'annual'
)),
    
    -- Availability metrics
    availability_percent DECIMAL(5, 2),
    uptime_minutes INTEGER,
    downtime_minutes INTEGER,
    planned_downtime_minutes INTEGER,
    unplanned_downtime_minutes INTEGER,
    
    -- Incident metrics
    incidents_total INTEGER DEFAULT 0,
    incidents_p1 INTEGER DEFAULT 0,
    incidents_p2 INTEGER DEFAULT 0,
    incidents_p3 INTEGER DEFAULT 0,
    incidents_p4 INTEGER DEFAULT 0,
    incidents_opened INTEGER DEFAULT 0,
    incidents_closed INTEGER DEFAULT 0,
    incidents_breached INTEGER DEFAULT 0,
    
    -- Performance metrics
    mttr_minutes DECIMAL(10, 2),
    mtbf_hours DECIMAL(10, 2),
    mtta_minutes DECIMAL(10, 2),
    
    -- SLA compliance
    sla_compliance_percent DECIMAL(5, 2),
    sla_breaches INTEGER DEFAULT 0,
    sla_target_percent DECIMAL(5, 2) DEFAULT 99.0,
    
    -- Customer satisfaction
    customer_satisfaction DECIMAL(3, 2),
    survey_responses INTEGER,
    
    -- TAC metrics
    tac_cases_opened INTEGER DEFAULT 0,
    tac_cases_closed INTEGER DEFAULT 0,
    tac_avg_response_minutes DECIMAL(10, 2),
    tac_avg_resolution_hours DECIMAL(10, 2),
    
    -- Change metrics
    changes_total INTEGER DEFAULT 0,
    changes_successful INTEGER DEFAULT 0,
    changes_failed INTEGER DEFAULT 0,
    changes_backed_out INTEGER DEFAULT 0,
    
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(property_id, metric_date, metric_type)
);

COMMENT ON TABLE mgm.sla_metrics IS 
'Service level agreement metrics and KPIs'
;

-- Changes (RFC - Request 
for
 Change)
CREATE TABLE mgm.changes (
    change_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    change_number VARCHAR(50) UNIQUE NOT NULL,
    property_id UUID REFERENCES mgm.properties(property_id),
    title VARCHAR(500) NOT NULL,
    description TEXT,
    change_type VARCHAR(50) CHECK (change_type IN (
'standard'
, 
'normal'
, 
'emergency'
, 
'pre-approved'
)),
    category VARCHAR(100),
    risk_level VARCHAR(20) CHECK (risk_level IN (
'low'
, 
'medium'
, 
'high'
, 
'critical'
)),
    risk_assessment TEXT,
    status VARCHAR(50) DEFAULT 
'draft'
 CHECK (status IN (
'draft'
, 
'submitted'
, 
'pending-approval'
, 
'approved'
, 
'rejected'
, 
'scheduled'
, 
'in-progress'
, 
'implementing'
, 
'successful'
, 
'failed'
, 
'backed-out'
, 
'closed'
, 
'cancelled'
)),
    approval_status VARCHAR(50) CHECK (approval_status IN (
'pending'
, 
'approved'
, 
'rejected'
, 
'conditional'
)),
    
    -- People
    requested_by UUID REFERENCES mgm.users(user_id),
    approved_by UUID REFERENCES mgm.users(user_id),
    implemented_by UUID REFERENCES mgm.users(user_id),
    change_manager UUID REFERENCES mgm.users(user_id),
    
    -- Timing
    scheduled_start TIMESTAMP WITH TIME ZONE,
    scheduled_end TIMESTAMP WITH TIME ZONE,
    estimated_duration INTERVAL,
    actual_start TIMESTAMP WITH TIME ZONE,
    actual_end TIMESTAMP WITH TIME ZONE,
    actual_duration INTERVAL,
    
    -- Impact
    affected_devices JSONB DEFAULT 
'[]'
,
    affected_services TEXT[],
    affected_users_count INTEGER,
    business_impact VARCHAR(50) CHECK (business_impact IN (
'none'
, 
'low'
, 
'medium'
, 
'high'
, 
'critical'
)),
    expected_downtime INTERVAL,
    actual_downtime INTERVAL,
    
    -- Plans
    implementation_plan TEXT,
    test_plan TEXT,
    rollback_plan TEXT,
    communication_plan TEXT,
    
    -- Results
    implementation_notes TEXT,
    success_criteria TEXT,
    test_results TEXT,
    lessons_learned TEXT,
    
    -- CAB (Change Advisory Board)
    cab_review_date TIMESTAMP WITH TIME ZONE,
    cab_decision TEXT,
    cab_attendees JSONB DEFAULT 
'[]'
,
    
    -- Related items
    related_incidents UUID[],
    related_changes UUID[],
    parent_change_id UUID REFERENCES mgm.changes(change_id),
    
    tags TEXT[],
    attachments JSONB DEFAULT 
'[]'
,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

COMMENT ON TABLE mgm.changes IS 
'Change requests and RFC tracking'
;

-- Teams Integration
CREATE TABLE mgm.teams_channels (
    channel_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES mgm.properties(property_id),
    incident_id UUID REFERENCES mgm.incidents(incident_id),
    channel_type VARCHAR(50) NOT NULL CHECK (channel_type IN (
'operations'
, 
'incidents'
, 
'alerts'
, 
'general'
, 
'property'
)),
    teams_channel_id VARCHAR(255) NOT NULL,
    teams_team_id VARCHAR(255) NOT NULL,
    channel_name VARCHAR(255) NOT NULL,
    channel_description TEXT,
    webhook_url TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_by UUID REFERENCES mgm.users(user_id),
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- WebEx Integration
CREATE TABLE mgm.webex_spaces (
    space_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    property_id UUID REFERENCES mgm.properties(property_id),
    incident_id UUID REFERENCES mgm.incidents(incident_id),
    tac_case_id UUID REFERENCES cisco.tac_cases(tac_case_id),
    space_type VARCHAR(50) NOT NULL CHECK (space_type IN (
'war-room'
, 
'incident'
, 
'operations'
, 
'general'
)),
    webex_space_id VARCHAR(255) NOT NULL,
    space_title VARCHAR(255) NOT NULL,
    meeting_url TEXT,
    meeting_number VARCHAR(100),
    meeting_password VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    started_at TIMESTAMP WITH TIME ZONE,
    ended_at TIMESTAMP WITH TIME ZONE,
    participants JSONB DEFAULT 
'[]'
,
    recording_urls JSONB DEFAULT 
'[]'
,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Notifications
CREATE TABLE mgm.notifications (
    notification_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES mgm.users(user_id) ON DELETE CASCADE,
    notification_type VARCHAR(50) NOT NULL CHECK (notification_type IN (
'incident'
, 
'tac_case'
, 
'change'
, 
'sla_breach'
, 
'license_expiry'
, 
'system'
, 
'alert'
)),
    category VARCHAR(50),
    title VARCHAR(500) NOT NULL,
    message TEXT,
    priority VARCHAR(20) DEFAULT 
'normal'
 CHECK (priority IN (
'low'
, 
'normal'
, 
'high'
, 
'urgent'
)),
    is_read BOOLEAN DEFAULT FALSE,
    read_at TIMESTAMP WITH TIME ZONE,
    action_url TEXT,
    action_text VARCHAR(100),
    related_entity_type VARCHAR(50),
    related_entity_id UUID,
    channels TEXT[] DEFAULT ARRAY[
'in-app'
],
    metadata JSONB DEFAULT 
'{}'
,
    expires_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_notifications_user_unread ON mgm.notifications(user_id, is_read, created_at DESC);

-- Dashboards (User customization)
CREATE TABLE mgm.dashboards (
    dashboard_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES mgm.users(user_id) ON DELETE CASCADE,
    dashboard_name VARCHAR(255) NOT NULL,
    dashboard_type VARCHAR(50) CHECK (dashboard_type IN (
'personal'
, 
'shared'
, 
'property'
, 
'executive'
)),
    layout JSONB NOT NULL DEFAULT 
'{}'
,
    widgets JSONB NOT NULL DEFAULT 
'[]'
,
    filters JSONB DEFAULT 
'{}'
,
    is_default BOOLEAN DEFAULT FALSE,
    is_public BOOLEAN DEFAULT FALSE,
    shared_with UUID[],
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Reports
CREATE TABLE mgm.reports (
    report_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_name VARCHAR(255) NOT NULL,
    report_type VARCHAR(50) CHECK (report_type IN (
'sla'
, 
'incident'
, 
'technology'
, 
'license'
, 
'executive'
, 
'custom'
)),
    description TEXT,
    report_config JSONB NOT NULL DEFAULT 
'{}'
,
    schedule_config JSONB,
    is_scheduled BOOLEAN DEFAULT FALSE,
    recipients TEXT[],
    format VARCHAR(20) CHECK (format IN (
'pdf'
, 
'excel'
, 
'csv'
, 
'json'
)) DEFAULT 
'pdf'
,
    created_by UUID REFERENCES mgm.users(user_id),
    last_generated_at TIMESTAMP WITH TIME ZONE,
    next_scheduled_at TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT 
'{}'
,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Report History
CREATE TABLE mgm.report_history (
    history_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    report_id UUID REFERENCES mgm.reports(report_id) ON DELETE CASCADE,
    generated_by UUID REFERENCES mgm.users(user_id),
    file_url TEXT,
    file_size BIGINT,
    status VARCHAR(50) CHECK (status IN (
'pending'
, 
'generating'
, 
'completed'
, 
'failed'
)),
    error_message TEXT,
    parameters JSONB DEFAULT 
'{}'
,
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================================
-- AUDIT & LOGGING
-- ============================================================================

CREATE TABLE audit.activity_log (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES mgm.users(user_id),
    action VARCHAR(100) NOT NULL,
    action_type VARCHAR(50) CHECK (action_type IN (
'create'
, 
'read'
, 
'update'
, 
'delete'
, 
'login'
, 
'logout'
, 
'access'
)),
    entity_type VARCHAR(100),
    entity_id UUID,
    entity_name VARCHAR(255),
    old_values JSONB,
    new_values JSONB,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(100),
    session_id VARCHAR(100),
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_log_user ON audit.activity_log(user_id, created_at DESC);
CREATE INDEX idx_activity_log_entity ON audit.activity_log(entity_type, entity_id);
CREATE INDEX idx_activity_log_action ON audit.activity_log(action_type, created_at DESC);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON mgm.users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_properties_updated_at BEFORE UPDATE ON mgm.properties
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_devices_updated_at BEFORE UPDATE ON mgm.devices
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_incidents_updated_at BEFORE UPDATE ON mgm.incidents
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_tac_cases_updated_at BEFORE UPDATE ON cisco.tac_cases
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_technologies_updated_at BEFORE UPDATE ON cisco.technologies
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_adoption_updated_at BEFORE UPDATE ON mgm.property_technology_adoption
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_licenses_updated_at BEFORE UPDATE ON cisco.licenses
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_changes_updated_at BEFORE UPDATE ON mgm.changes
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_dashboards_updated_at BEFORE UPDATE ON mgm.dashboards
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_reports_updated_at BEFORE UPDATE ON mgm.reports
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to generate incident number
CREATE OR REPLACE FUNCTION generate_incident_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.incident_number IS NULL THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(incident_number FROM 5) AS INTEGER)), 0) + 1
        INTO next_num
        FROM mgm.incidents
        WHERE incident_number ~ 
'^INC-[0-9]+$'
;
        
        NEW.incident_number := 
'INC-'
 || LPAD(next_num::TEXT, 6, 
'0'
);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_incident_number_trigger
    BEFORE INSERT ON mgm.incidents
    FOR EACH ROW EXECUTE FUNCTION generate_incident_number();

-- Function to generate change number
CREATE OR REPLACE FUNCTION generate_change_number()
RETURNS TRIGGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    IF NEW.change_number IS NULL THEN
        SELECT COALESCE(MAX(CAST(SUBSTRING(change_number FROM 5) AS INTEGER)), 0) + 1
        INTO next_num
        FROM mgm.changes
        WHERE change_number ~ 
'^CHG-[0-9]+$'
;
        
        NEW.change_number := 
'CHG-'
 || LPAD(next_num::TEXT, 6, 
'0'
);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER generate_change_number_trigger
    BEFORE INSERT ON mgm.changes
    FOR EACH ROW EXECUTE FUNCTION generate_change_number();

-- Function to calculate incident resolution 
time

CREATE OR REPLACE FUNCTION calculate_resolution_time()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.resolved_at IS NOT NULL AND OLD.resolved_at IS NULL THEN
        NEW.resolution_time := NEW.resolved_at - NEW.opened_at;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER calculate_incident_resolution
    BEFORE UPDATE ON mgm.incidents
    FOR EACH ROW EXECUTE FUNCTION calculate_resolution_time();

COMMIT;
EOF