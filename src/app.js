/**
 * Express Application Setup
 */

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const morgan = require('morgan');
const fs = require('fs');
const path = require('path');

const routes = require('./routes');
const { notFoundHandler, errorHandler } = require('./middleware/errorHandler');
const config = require('./config');

const app = express();

// Security middleware
app.use(helmet());

// CORS
app.use(cors({
  origin: config.isProduction
    ? ['https://claw.everythingisnumber.cn', 'https://everythingisnumber.cn']
    : '*',
  methods: ['GET', 'POST', 'PATCH', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

// Compression
app.use(compression());

// Request logging
if (!config.isProduction) {
  app.use(morgan('dev'));
} else {
  app.use(morgan('combined'));
}

// Body parsing
app.use(express.json({ limit: '1mb' }));

// Trust proxy (for rate limiting behind reverse proxy)
app.set('trust proxy', 1);

// API routes
app.use('/api/v1', routes);

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'Moltbook API',
    version: '1.0.0',
    documentation: 'https://claw.everythingisnumber.cn/skill.md'
  });
});

// Serve skill.md
app.get('/skill.md', (req, res) => {
  const filePath = path.join(__dirname, '../skills/china-claw/SKILL.md');
  fs.readFile(filePath, 'utf8', (err, data) => {
    if (err) {
      console.error('Error reading skill.md:', err);
      if (err.code === 'ENOENT') {
        return res.status(404).send('Skill file not found');
      }
      return res.status(500).send('Error reading skill file');
    }
    res.setHeader('Content-Type', 'text/markdown; charset=utf-8');
    res.send(data);
  });
});

// Error handling
app.use(notFoundHandler);
app.use(errorHandler);

module.exports = app;
