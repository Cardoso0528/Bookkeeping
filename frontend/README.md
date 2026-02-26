# Bookkeeping App Frontend

A modern, responsive web application for managing business finances.

## Features

- 📊 **Dashboard** - Financial overview with key metrics
- 💰 **Transactions** - Manage income and expenses with filtering
- 🏦 **Accounts** - Track multiple bank accounts and credit cards
- 📁 **Categories** - Organize transactions with custom categories
- 🎨 **Modern UI** - Beautiful design with TailwindCSS
- 📱 **Responsive** - Works on desktop, tablet, and mobile

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **TailwindCSS** for styling
- **React Router** for navigation
- **Lucide React** for icons
- **date-fns** for date formatting

## Getting Started

### Prerequisites

- Node.js 18+ and npm

### Installation

1. Install dependencies:
   ```bash
   npm install
   ```

2. Create environment file:
   ```bash
   cp .env.example .env
   ```

3. Update the API URL in `.env`:
   ```
   VITE_API_URL=http://localhost:8080/api
   ```

### Development

Start the development server:

```bash
npm run dev
```

The app will be available at `http://localhost:5173`

### Build for Production

```bash
npm run build
```

The production-ready files will be in the `dist` folder.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
frontend/
├── src/
│   ├── components/      # Reusable components
│   │   └── Layout.tsx   # Main layout with navigation
│   ├── pages/           # Page components
│   │   ├── Dashboard.tsx
│   │   ├── Transactions.tsx
│   │   ├── Accounts.tsx
│   │   └── Categories.tsx
│   ├── services/        # API services
│   │   └── api.ts       # API client
│   ├── types/           # TypeScript types
│   │   └── index.ts     # Type definitions
│   ├── App.tsx          # Main app component
│   ├── main.tsx         # Entry point
│   └── index.css        # Global styles
├── public/              # Static assets
└── index.html           # HTML template
```

## API Integration

The app is ready to integrate with your Spring Boot backend. Update the API endpoints in `src/services/api.ts` to match your backend routes.

Currently using mock data for demonstration. Replace with actual API calls:

```typescript
// Example: Replace mock data with real API call
const transactions = await transactionApi.getAll(filters);
```

## Features to Implement

- [ ] Add/Edit/Delete modals for all entities
- [ ] Real-time data updates
- [ ] Advanced filtering and search
- [ ] Data visualization (charts)
- [ ] CSV import/export
- [ ] Authentication and authorization
- [ ] Dark mode support
- [ ] Notifications and alerts

## Contributing

Feel free to customize and extend the application based on your needs!
