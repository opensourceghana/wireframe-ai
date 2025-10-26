# AI Wireframing Tool

A powerful AI-powered wireframing tool that generates wireframes from text descriptions using Hugging Face models.

## Features

- **Text-to-Wireframe Generation**: Describe your wireframe in natural language
- **Multiple Styles**: Low-fi, high-fi, mobile, and web layouts
- **SVG & PNG Export**: Download wireframes in multiple formats
- **Real-time Preview**: See your wireframes instantly
- **Modern UI**: Clean, responsive interface built with React and Tailwind CSS

## Architecture

This project uses a hybrid approach combining:
- **ControlNet Wireframe** for AI generation
- **FastAPI** backend for model inference
- **React + TypeScript** frontend for user interface
- **Tailwind CSS** for modern styling

## Quick Start

### Prerequisites

- Python 3.9+ with GPU support (recommended)
- Node.js 18+
- 16GB+ RAM for model inference

### Backend Setup

```bash
cd backend
pip install -r requirements.txt
python main.py
```

The backend will start on `http://localhost:8000`

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:3000`

## Usage

1. **Enter Description**: Describe your wireframe (e.g., "Login page with email field, password field, and submit button")
2. **Select Style**: Choose from low-fi, high-fi, mobile, or web layouts
3. **Generate**: Click "Generate Wireframe" and wait for AI processing
4. **Download**: Export as SVG or PNG format

## Example Prompts

- "E-commerce product page with image gallery, price, and add to cart button"
- "Dashboard with sidebar navigation, charts, and data tables"
- "Mobile app login screen with social media login options"
- "Landing page with hero section, features, and contact form"

## API Endpoints

- `POST /generate-wireframe` - Generate wireframe from prompt
- `GET /wireframe-styles` - Get available wireframe styles
- `GET /health` - Check API health status

## Development

### Backend Development
```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm run dev
```

## Model Information

- **Primary Model**: ControlNet Wireframe (Jise/controlnet-wireframe)
- **Base Model**: Stable Diffusion v1.5
- **Training Data**: Mobile UI Design Dataset (7,846 images)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

MIT License - see LICENSE file for details

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**: Reduce batch size or use CPU inference
2. **Model Loading Errors**: Ensure sufficient disk space and internet connection
3. **Frontend Build Errors**: Clear node_modules and reinstall dependencies

### Performance Tips

- Use GPU for faster generation (CUDA recommended)
- Cache models locally to avoid re-downloading
- Optimize image sizes for better performance

## Roadmap

- [ ] Sketch-to-wireframe enhancement
- [ ] Conversational wireframe refinement
- [ ] Component library integration
- [ ] Real-time collaborative editing
- [ ] Advanced export options (Figma, Sketch)

## Support

For issues and questions, please open a GitHub issue or contact the development team.
