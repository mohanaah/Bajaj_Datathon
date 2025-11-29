# Deployment Guide

## Quick Deployment Options

### Option 1: Railway (Recommended - Easiest)

1. Go to https://railway.app
2. Sign up/login with GitHub
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repository
5. Railway auto-detects Python and installs dependencies
6. Add environment variables:
   - `GROQ_API_KEY=your_key_here`
   - `OPENAI_API_KEY` (optional)
   - `ANTHROPIC_API_KEY` (optional)
7. Your API will be live at: `https://your-app-name.up.railway.app`

**Endpoint URL**: `https://your-app-name.up.railway.app/extract-bill-data`

---

### Option 2: Render (Free Tier Available)

1. Go to https://render.com
2. Sign up/login with GitHub
3. Click "New" → "Web Service"
4. Connect your GitHub repository
5. Settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3
6. Add environment variables in the dashboard
7. Deploy!

**Endpoint URL**: `https://your-app-name.onrender.com/extract-bill-data`

---

### Option 3: Fly.io (Good for Global Distribution)

1. Install Fly CLI: `curl -L https://fly.io/install.sh | sh`
2. Login: `fly auth login`
3. Create app: `fly launch`
4. Deploy: `fly deploy`
5. Your API will be at: `https://your-app-name.fly.dev`

**Endpoint URL**: `https://your-app-name.fly.dev/extract-bill-data`

---

### Option 4: Heroku (Classic Option)

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables: `heroku config:set GROQ_API_KEY=your_key`
5. Deploy: `git push heroku main`

**Endpoint URL**: `https://your-app-name.herokuapp.com/extract-bill-data`

---

## Environment Variables to Set

Make sure to set these in your deployment platform:

```bash
GROQ_API_KEY=
OPENAI_API_KEY=your_key_here  # Optional
ANTHROPIC_API_KEY=your_key_here  # Optional
```

---

## Testing Your Deployed API

Once deployed, test with:

```bash
curl -X POST "https://your-deployed-url.com/extract-bill-data" \
  -H "Content-Type: application/json" \
  -d '{
    "document": "https://hackrx.blob.core.windows.net/assets/datathon-IIT/sample_2.png?sv=2025-07-05&spr=https&st=2025-11-24T14%3A13%3A22Z&se=2026-11-25T14%3A13%3A00Z&sr=b&sp=r&sig=WFJYfNw0PJdZOpOYlsoAW0XujYGG1x2HSbcDREiFXSU%3D"
  }' | python -m json.tool
```

---

## Netlify (Not Recommended for FastAPI)

If you deployed to Netlify:

- **Your URL**: Check https://app.netlify.com → Your site → Overview
- **Limitation**: Netlify Functions have 10-second timeout (too short for OCR)
- **Recommendation**: Use Railway or Render instead

---

## Important Notes

1. **Tesseract OCR**: Most cloud platforms don't have Tesseract pre-installed. You may need to:

   - Use a Dockerfile with Tesseract installed
   - Or use a cloud OCR service instead
   - Or deploy on a VM (DigitalOcean, AWS EC2)

2. **PDF Processing**: `pdf2image` requires `poppler-utils` which also needs to be installed

3. **File Size Limits**: Check your platform's limits for file uploads/downloads
