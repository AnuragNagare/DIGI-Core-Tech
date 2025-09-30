# Smart Grocery App

A comprehensive grocery management app with AI-powered recipe suggestions, meal planning, and inventory tracking.

## Features

- 📦 Inventory Management with expiry tracking
- 🤖 AI-powered recipe suggestions
- 📅 Weekly meal planning
- 🛒 Smart shopping lists
- 📊 Analytics and waste tracking
- 🔔 Expiry alerts and notifications

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

1. Clone or download the project
2. Install dependencies:
   \`\`\`bash
   npm install
   # or
   yarn install
   \`\`\`

3. Run the development server:
   \`\`\`bash
   npm run dev
   # or
   yarn dev
   \`\`\`

4. Open [http://localhost:3000](http://localhost:3000) in your browser

### Building for Production

\`\`\`bash
npm run build
npm start
\`\`\`

## Tech Stack

- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + shadcn/ui
- **Icons**: Lucide React
- **Date Handling**: date-fns

## Project Structure

\`\`\`
├── app/                 # Next.js app directory
│   ├── api/            # API routes
│   ├── globals.css     # Global styles
│   ├── layout.tsx      # Root layout
│   └── page.tsx        # Main app component
├── lib/                # Utility functions and types
│   ├── types.ts        # TypeScript type definitions
│   ├── api.ts          # API utilities
│   └── hooks/          # Custom React hooks
└── components/         # Reusable UI components (auto-generated)
\`\`\`

## Development

This project is set up to work seamlessly with modern development tools like Cursor, VS Code, and other TypeScript-aware editors.

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Run TypeScript compiler check

## Backend Integration

The frontend is ready for backend integration with:
- RESTful API endpoints in `/app/api`
- TypeScript interfaces for data models
- Custom hooks for data fetching
- Error handling and loading states

Ready to connect with any database (PostgreSQL, MongoDB, etc.) and ORM (Prisma, Drizzle, etc.).
