const express = require('express');
const cors = require('cors');
const app = express();
const port = process.env.PORT || 3030;

// Налаштування CORS для віджету
app.use(cors({
  origin: '*', // Дозволяємо всі домени для віджету
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
}));

app.use(express.json());

// Статичні файли для віджету
app.use('/widget', express.static('public'));
app.use('/', express.static('public'));

// API endpoints для віджету
app.get('/api/chat', (req, res) => {
  res.json({
    message: 'Chat endpoint ready',
    timestamp: new Date().toISOString()
  });
});

app.post('/api/chat', async (req, res) => {
  try {
    const { message, api_spec_url } = req.body;

    // Тут буде логіка обробки запиту через AI Swagger Bot
    const response = {
      id: Date.now(),
      message: `AI Bot: Отримано запит: "${message}"`,
      timestamp: new Date().toISOString(),
      type: 'bot'
    };

    res.json(response);
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
});

// Health check
app.get('/health', (req, res) => {
  res.json({ status: 'OK', timestamp: new Date().toISOString() });
});

// Віджет HTML
app.get('/widget', (req, res) => {
  res.sendFile(__dirname + '/public/widget.html');
});

app.listen(port, () => {
  console.log(`🚀 API Service running on port ${port}`);
  console.log(`📦 Widget available at: http://localhost:${port}/widget`);
});
