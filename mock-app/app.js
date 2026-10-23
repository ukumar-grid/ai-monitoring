const express = require('express');
const client = require('prom-client');

const app = express();
const register = new client.Registry();

// Default metrics (CPU, Memory, Event Loop delay)
client.collectDefaultMetrics({ register });

// Custom Prometheus Metrics
const httpRequestDurationMicroseconds = new client.Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'code'],
  buckets: [0.1, 0.3, 0.5, 1, 1.5, 3, 5]
});

const httpRequestsTotal = new client.Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'code']
});

register.registerMetric(httpRequestDurationMicroseconds);
register.registerMetric(httpRequestsTotal);

let isSpikeActive = false;
let memoryLeakArray = [];

// Endpoint to simulate normal traffic
app.get('/api/checkout', (req, res) => {
  const end = httpRequestDurationMicroseconds.startTimer();
  const statusCode = isSpikeActive && Math.random() < 0.6 ? 500 : 200;
  
  setTimeout(() => {
    httpRequestsTotal.inc({ method: 'GET', route: '/api/checkout', code: statusCode });
    end({ method: 'GET', route: '/api/checkout', code: statusCode });
    res.status(statusCode).json({ status: statusCode === 200 ? 'success' : 'internal_error' });
  }, isSpikeActive ? Math.random() * 2000 : Math.random() * 200);
});

// Chaos endpoints to trigger incidents
app.post('/chaos/error-spike/enable', (req, res) => {
  isSpikeActive = true;
  res.json({ message: 'Error spike enabled on /api/checkout' });
});

app.post('/chaos/error-spike/disable', (req, res) => {
  isSpikeActive = false;
  res.json({ message: 'Error spike disabled' });
});

// Expose Prometheus metrics
app.get('/metrics', async (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(await register.metrics());
});

app.listen(3000, () => {
  console.log('Mock target running on port 3000');
});