# Museum Interaction Platform

A full-stack web application that enables museums to upload bulk images, transcribe them using Claude AI, and generate engaging educational content including flashcards, infographics, video scripts, and podcast formats.

## Features

- 📸 **Bulk Image Upload**: Drag-and-drop interface for uploading multiple museum images
- 🤖 **AI Transcription**: Automatic text extraction from images using Claude Sonnet 4
- 📚 **Flashcard Generation**: Create Q&A flashcards for educational purposes
- 📊 **Infographic Creation**: Generate structured summaries perfect for visual presentations
- 🎬 **Video Scripts**: Create narration scripts for educational videos
- 🎙️ **Podcast Formatting**: Format content for podcast or audio narration
- 📈 **Real-time Progress**: Track transcription progress with live updates
- 💾 **Multiple Formats**: Download transcriptions and generated content in various formats

## Architecture

- **Frontend**: Next.js 14+ with TypeScript and Tailwind CSS
- **Backend**: FastAPI (Python) with async processing
- **AI**: Anthropic Claude Sonnet 4 API
- **Storage**: Local file system (easily configurable for cloud storage)

## Prerequisites

- Python 3.8+
- Node.js 18+
- Anthropic API key ([Get one here](https://console.anthropic.com/))

## Installation

### 1. Clone the Repository

```bash
git clone <repository-url>
cd museum-interaction-platform
```

### 2. Backend Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Frontend Setup

```bash
cd frontend
npm install
cd ..
```

### 4. Environment Configuration

Create a `.env` file in the project root:

```bash
cp .env.example .env
```

Edit `.env` and add your Anthropic API key:

```
ANTHROPIC_API_KEY=your-api-key-here
BACKEND_HOST=localhost
BACKEND_PORT=8000
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Usage

### Start the Backend

```bash
# Activate virtual environment if not already active
source venv/bin/activate

# Start FastAPI server
cd backend
python -m uvicorn app.main:app --reload --host localhost --port 8000
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`

### Start the Frontend

```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`

### Using the Application

1. **Upload Images**: Drag and drop or select multiple image files
2. **Wait for Transcription**: The system automatically processes images and extracts text
3. **Select Content Types**: Choose which content formats to generate
4. **Download Results**: Download transcriptions and generated content

## Project Structure

```
museum-interaction-platform/
├── backend/
│   ├── app/
│   │   ├── api/              # API routes and models
│   │   ├── core/              # Configuration
│   │   ├── services/          # Business logic
│   │   └── main.py            # FastAPI app entry point
│   ├── uploads/               # Temporary upload storage
│   └── outputs/               # Generated content storage
├── frontend/
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   └── lib/                   # API client utilities
├── image_transcriber.py       # Core transcription logic
├── .env.example               # Environment variable template
└── README.md                  # This file
```

## API Endpoints

- `POST /api/upload` - Upload images for transcription
- `POST /api/transcribe/{job_id}` - Start transcription job
- `GET /api/job/{job_id}/status` - Get job status
- `GET /api/job/{job_id}/results` - Get transcription results
- `POST /api/generate-content` - Generate educational content
- `GET /api/download/{job_id}/{file_type}` - Download generated files

## Security

- API keys are stored in `.env` file (gitignored)
- Never commit `.env` files to version control
- File uploads are validated for type and size
- CORS is configured for frontend domain only

## Development

### Backend Development

```bash
cd backend
python -m uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm run dev
```

### Running Tests

```bash
# Backend tests (when implemented)
cd backend
pytest

# Frontend tests (when implemented)
cd frontend
npm test
```

## Deployment

### Backend Deployment

1. Set environment variables on your hosting platform
2. Install dependencies: `pip install -r backend/requirements.txt`
3. Run with: `uvicorn app.main:app --host 0.0.0.0 --port 8000`

### Frontend Deployment

1. Set `NEXT_PUBLIC_API_URL` environment variable
2. Build: `npm run build`
3. Start: `npm start`

Or deploy to Vercel:

```bash
cd frontend
vercel
```

## Cost Estimates

Using Claude Sonnet 4:
- ~$0.003 per image for transcription
- ~$0.01-0.02 per content generation (flashcards, infographics, etc.)
- Example: 100 images + 4 content types ≈ $0.50 total

## Troubleshooting

### API Key Issues
- Ensure `.env` file exists and contains `ANTHROPIC_API_KEY`
- Check that the API key is valid and has credits

### Upload Failures
- Check file size limits (default: 100MB per file)
- Verify file types are supported (JPG, PNG, GIF, WEBP, BMP)

### Backend Connection Issues
- Ensure backend is running on port 8000
- Check `NEXT_PUBLIC_API_URL` matches backend URL

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - feel free to modify and use as needed!

## Support

For issues or questions, please open an issue on GitHub.

## Acknowledgments

- Built with [Next.js](https://nextjs.org/)
- Powered by [FastAPI](https://fastapi.tiangolo.com/)
- AI capabilities provided by [Anthropic Claude](https://www.anthropic.com/)
