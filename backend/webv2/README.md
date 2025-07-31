# Hexy WebV2

A clean, modern web interface for the Hexy world generator built with TypeScript and Vite.

## Architecture

The new webv2 project follows a clean architecture pattern with clear separation of concerns:

### Structure

```
src/
├── components/          # UI Components
│   ├── Header.ts       # Navigation header
│   ├── WorldGrid.ts    # Hexagonal world grid display
│   └── HexContent.ts   # Hex content details panel
├── services/           # Business Logic Services
│   ├── WorldGridService.ts    # World grid state management
│   └── HexContentService.ts   # Hex content management
├── api/                # API Communication
│   └── client.ts       # API client for backend communication
├── models/             # Type Definitions
│   └── types.ts        # TypeScript interfaces and types
├── styles/             # CSS Styles
│   ├── globals.css     # Global styles
│   └── fonts.css       # Font definitions
└── main.ts             # Application entry point
```

### Key Features

- **Clean Architecture**: Separation of concerns with services, components, and models
- **Type Safety**: Full TypeScript support with strict type checking
- **Modern Build**: Vite for fast development and building
- **Responsive Design**: Clean, modern UI with proper responsive layout
- **Service Layer**: Centralized state management through services
- **API Integration**: Clean API client for backend communication

### Components

#### Header
- Navigation between World and Cities views
- Clean, modern design with active state indicators

#### WorldGrid
- Displays hexagonal world grid
- Handles hex selection and interaction
- Responsive grid layout with proper hex rendering

#### HexContent
- Displays detailed information about selected hexes
- Supports both world and city hex content
- Clean, readable content presentation

### Services

#### WorldGridService
- Manages world grid state
- Handles hex selection
- Provides grid operations (load, generate, etc.)

#### HexContentService
- Manages hex content display
- Handles view mode switching
- Provides content formatting and display logic

### API Client

The API client provides a clean interface for backend communication:
- Type-safe API calls
- Error handling
- Response formatting
- Support for all backend endpoints

## Development

### Prerequisites

- Node.js 18+
- npm or yarn

### Setup

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start development server:
   ```bash
   npm run dev
   ```

3. Build for production:
   ```bash
   npm run build
   ```

### Scripts

- `npm run dev` - Start development server with hot reload
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run type-check` - Run TypeScript type checking

## Integration

The webv2 project is designed to work alongside the existing backend:

- **Port**: Runs on port 3001 (configurable in vite.config.ts)
- **API Proxy**: Automatically proxies `/api` requests to backend on port 5000
- **Backend Integration**: Uses the same API endpoints as the original web interface

## Migration Path

This new architecture provides a foundation for progressively migrating features:

1. **Phase 1**: Basic world grid display and hex selection ✅
2. **Phase 2**: Enhanced hex content display
3. **Phase 3**: City overlay integration
4. **Phase 4**: Advanced features and optimizations

## Design Principles

- **Simplicity**: Clean, readable code with minimal complexity
- **Type Safety**: Full TypeScript usage with strict typing
- **Separation of Concerns**: Clear boundaries between UI, business logic, and data
- **Modern Patterns**: Use of modern JavaScript/TypeScript features
- **Performance**: Efficient rendering and state management 