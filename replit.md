# replit.md

## Overview

This is a simple AI chatbot application built with Flask and OpenAI's GPT API. The application provides a web-based chat interface where users can interact with an AI assistant in French. It uses Replit's AI integrations to connect to OpenAI's API.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Entry Point**: `main.py` serves as the single backend file
- **API Design**: Simple REST API with two endpoints:
  - `GET /` - Serves the chat interface HTML
  - `POST /chat` - Handles chat messages and returns AI responses

### Frontend Architecture
- **Approach**: Server-side rendered single HTML template with embedded CSS and JavaScript
- **Location**: `templates/index.html`
- **Design Pattern**: Vanilla JavaScript with async/await for API calls
- **UI**: Minimal chat interface with message bubbles (user messages in blue, bot messages in gray)

### AI Integration
- **Provider**: OpenAI API via Replit's AI integrations
- **Model**: GPT-5
- **Configuration**: Uses environment variables for API key and base URL (`AI_INTEGRATIONS_OPENAI_API_KEY`, `AI_INTEGRATIONS_OPENAI_BASE_URL`)
- **System Prompt**: French-language friendly assistant persona

### Error Handling
- Basic error handling with JSON error responses
- Server-side logging for API errors

## External Dependencies

### Python Packages
- **Flask**: Web framework for routing and templating
- **OpenAI**: Official Python client for OpenAI API

### External Services
- **Replit AI Integrations**: Provides OpenAI API access through environment variables
- **OpenAI GPT-5**: Language model for generating chat responses

### Environment Variables Required
- `AI_INTEGRATIONS_OPENAI_API_KEY`: API key for OpenAI access
- `AI_INTEGRATIONS_OPENAI_BASE_URL`: Base URL for the OpenAI API endpoint