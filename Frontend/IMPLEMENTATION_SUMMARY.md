# NANS Frontend - Production-Grade Implementation

## Project Overview

This is a comprehensive, production-grade frontend implementation for the National Association Management Platform (NANS). Built with modern technologies and enterprise design patterns, it provides a complete user interface for the NANS system serving Admin, General Secretary, Chairman, and Member roles.

## Technology Stack

- **Framework**: Next.js 15.0.0 with React 19
- **Language**: TypeScript 5.3.3 (Strict Mode)
- **Styling**: Tailwind CSS 3.3.6 with custom theme
- **State Management**: Zustand v4.4.1 (UI state) + React Query v5.28.0 (Server state)
- **Forms**: React Hook Form v7.51.0 + Zod v3.22.4
- **HTTP Client**: Axios v1.6.2 with custom interceptors
- **Animations**: Framer Motion v10.16.16
- **Icons**: Lucide React v0.294.0
- **Date Handling**: date-fns v2.30.0
- **PDF Generation**: jsPDF v2.5.1
- **QR Code**: HTML5-QRCode v2.3.8

## Project Structure

```
Frontend/
├── src/
│   ├── app/                          # Next.js App Router pages
│   │   ├── layout.tsx               # Root layout
│   │   ├── auth/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/page.tsx       # Main dashboard
│   │   ├── members/
│   │   │   ├── page.tsx             # Members list
│   │   │   ├── [id]/page.tsx        # Member profile
│   │   │   └── approve/page.tsx     # Approval queue
│   │   ├── meetings/page.tsx        # Meetings list
│   │   ├── activities/page.tsx      # Activities list
│   │   ├── documents/page.tsx       # Documents library
│   │   ├── my-id-card/page.tsx      # Digital ID card
│   │   ├── profile/page.tsx         # User profile
│   │   └── settings/page.tsx        # Settings
│   │
│   ├── components/
│   │   ├── ui/                      # Reusable UI components
│   │   │   ├── button.tsx           # Button with variants
│   │   │   ├── card.tsx             # Card container
│   │   │   ├── input.tsx            # Text input
│   │   │   ├── textarea.tsx         # Text area
│   │   │   └── badge.tsx            # Badge component
│   │   │
│   │   └── layout/                  # Layout components
│   │       ├── sidebar.tsx          # Role-aware sidebar
│   │       ├── dashboard-layout.tsx # Protected dashboard wrapper
│   │       └── auth-layout.tsx      # Auth pages wrapper
│   │
│   ├── features/                    # Feature-specific components
│   │   ├── auth/
│   │   │   └── components/
│   │   │       ├── login-form.tsx
│   │   │       └── register-form.tsx
│   │   ├── dashboard/
│   │   │   ├── dashboard-content.tsx
│   │   │   ├── admin-dashboard.tsx
│   │   │   ├── general-secretary-dashboard.tsx
│   │   │   ├── chairman-dashboard.tsx
│   │   │   └── member-dashboard.tsx
│   │   ├── members/
│   │   │   └── components/
│   │   │       ├── members-list.tsx
│   │   │       ├── member-profile.tsx
│   │   │       └── member-approval-queue.tsx
│   │   ├── meetings/
│   │   │   └── components/
│   │   │       └── meetings-list.tsx
│   │   ├── activities/
│   │   │   └── components/
│   │   │       └── activities-list.tsx
│   │   ├── documents/
│   │   │   └── components/
│   │   │       └── documents-list.tsx
│   │   ├── id-card/
│   │   │   └── digital-id-card.tsx
│   │   ├── profile/
│   │   │   └── user-profile.tsx
│   │   └── settings/
│   │       └── settings-content.tsx
│   │
│   ├── lib/
│   │   ├── api-client.ts           # Axios client with interceptors
│   │   ├── config.ts               # API configuration & routes
│   │   ├── cn.ts                   # Utility for class names
│   │   └── utils.ts                # Utility functions
│   │       ├── tokenUtils
│   │       ├── userUtils
│   │       ├── dateUtils
│   │       ├── stringUtils
│   │       ├── numberUtils
│   │       ├── validationUtils
│   │       ├── errorUtils
│   │       └── collectionUtils
│   │
│   ├── hooks/                      # Custom React hooks
│   │   ├── use-auth.ts            # Auth mutations & queries
│   │   └── use-members.ts         # Member queries & mutations
│   │
│   ├── services/                   # API service layer
│   │   ├── auth.ts                # Auth API methods
│   │   ├── members.ts             # Member API methods
│   │   └── index.ts               # Meeting, Activity, Document APIs
│   │
│   ├── store/                      # Zustand stores
│   │   └── auth.ts                # Auth state with persistence
│   │
│   ├── providers/
│   │   └── index.tsx              # React Query + Theme providers
│   │
│   ├── types/
│   │   └── index.ts               # All TypeScript interfaces & enums
│   │
│   └── styles/
│       └── globals.css            # Global styles & Tailwind directives
│
├── public/                         # Static assets
├── package.json                    # Dependencies
├── tsconfig.json                   # TypeScript configuration
├── tailwind.config.ts              # Tailwind theme configuration
├── next.config.js                  # Next.js configuration
├── postcss.config.js               # PostCSS configuration
├── .eslintrc.json                  # ESLint configuration
├── .env.example                    # Environment variables template
├── .env.local                      # Local environment variables
└── README.md                        # This file
```

## Key Features Implemented

### 1. Authentication System
- ✅ Login page with email/password
- ✅ Registration page with validation
- ✅ JWT token-based auth with refresh flow
- ✅ Automatic token refresh on 401 responses
- ✅ Protected routes with automatic redirect to login
- ✅ Persistent auth state with localStorage
- ✅ Failed request queue during token refresh

### 2. Role-Based Dashboard System
- ✅ **Admin Dashboard**: Total members, active members, suspended members, contribution hours, member breakdown
- ✅ **General Secretary Dashboard**: National statistics, pending approvals, meetings, documents
- ✅ **Chairman Dashboard**: Chapter members, pending approvals, meetings, activities
- ✅ **Member Dashboard**: Membership status, upcoming events, activity statistics

### 3. Member Management
- ✅ Members list with pagination and search
- ✅ Member profile view with detailed information
- ✅ Member approval queue for administrators
- ✅ Member activity statistics
- ✅ Member status tracking (active, inactive, suspended)

### 4. UI Component Library
- ✅ Button with variants (default, destructive, outline, secondary, ghost, link)
- ✅ Card container with header, content, footer sections
- ✅ Input field with accessibility features
- ✅ Textarea for longer form inputs
- ✅ Badge component with variants (default, secondary, destructive, outline, success, warning)
- ✅ Custom styling with Tailwind CSS

### 5. Navigation System
- ✅ Sidebar with role-aware menu items
- ✅ Mobile-responsive hamburger menu
- ✅ Active route highlighting
- ✅ Quick links for common actions
- ✅ User menu with logout

### 6. Additional Pages
- ✅ Digital ID Card display with QR code
- ✅ Meetings list with upcoming events
- ✅ Activities list with participation tracking
- ✅ Documents library with download capability
- ✅ User profile settings
- ✅ Application settings (theme, notifications, privacy)

### 7. Form Handling
- ✅ React Hook Form integration with Zod validation
- ✅ Real-time validation feedback
- ✅ Error message display
- ✅ Loading states during submission
- ✅ Success/error notifications

### 8. State Management
- ✅ Zustand store for auth state
- ✅ localStorage persistence with hydration safeguards
- ✅ React Query for server state management
- ✅ Automatic cache invalidation on mutations
- ✅ Request retry logic with configurable stale time

### 9. API Integration
- ✅ Custom Axios client with request/response interceptors
- ✅ Automatic Bearer token attachment
- ✅ Failed request queue during token refresh
- ✅ Comprehensive error handling
- ✅ Network error detection
- ✅ API configuration constants for easy endpoint management

### 10. Theming & Styling
- ✅ Light/Dark mode with next-themes
- ✅ CSS variables for theme colors
- ✅ Tailwind custom utilities
- ✅ Custom animations and transitions
- ✅ Responsive design for all screen sizes
- ✅ Glassmorphism effects and gradients

## Getting Started

### Prerequisites
- Node.js 18+ 
- npm or yarn package manager
- FastAPI backend running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Create .env.local from template
cp .env.example .env.local

# Update backend URL if needed in .env.local
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_API_BASE_PATH=/api/v1
```

### Running the Development Server

```bash
npm run dev
```

The application will be available at [http://localhost:3000](http://localhost:3000)

### Building for Production

```bash
npm run build
npm start
```

## Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm start` - Start production server
- `npm run lint` - Run ESLint
- `npm run type-check` - Check TypeScript types
- `npm run format` - Format code with Prettier

## API Integration

The frontend is configured to work with the FastAPI backend at:
- **Base URL**: http://localhost:8000
- **API Base Path**: /api/v1

### Key API Endpoints Used

**Authentication**
- POST `/auth/login` - User login
- POST `/auth/register` - User registration
- POST `/auth/refresh` - Token refresh
- GET `/auth/me` - Get current user

**Members**
- GET `/members` - List members (paginated)
- GET `/members/{id}` - Get member details
- POST `/members` - Create new member
- PUT `/members/{id}` - Update member
- GET `/members/stats` - Get statistics

**Meetings**
- GET `/meetings` - List meetings
- GET `/meetings/{id}` - Get meeting details
- POST `/meetings` - Create meeting

**Activities**
- GET `/activities` - List activities
- GET `/activities/{id}` - Get activity details
- POST `/activities` - Create activity

## User Roles & Permissions

The system supports 4 user roles with different feature access:

### Admin
- Full access to all features
- User management
- Audit logs
- System settings
- Member approval

### General Secretary
- Member management
- Meeting management
- Activity management
- Document management
- Member approval

### Chairman
- Chapter member management
- Chapter meeting management
- Chapter activity management
- Member approval for chapter

### Member
- View own profile
- View available meetings
- View activities
- View documents
- Download own ID card

## Authentication Flow

1. User enters credentials on login page
2. Frontend sends POST request to `/auth/login`
3. Backend returns `accessToken` and `refreshToken`
4. Tokens stored in localStorage
5. `accessToken` added to all API requests via Authorization header
6. When `accessToken` expires (401 response):
   - Automatic refresh token request
   - Failed requests queued
   - New `accessToken` obtained
   - Queued requests retried
7. On invalid refresh token:
   - Auth state cleared
   - User redirected to login

## Component Architecture

### UI Components
- Stateless, reusable components
- Built with CVA (class-variance-authority) for variant management
- Styled with Tailwind CSS
- Forward refs for DOM access

### Feature Components
- Organized by feature (members, meetings, activities, etc.)
- Use custom hooks for data fetching
- Handle loading, error, and empty states
- Responsive layout

### Layout Components
- DashboardLayout: Wraps protected pages with sidebar
- AuthLayout: Wraps authentication pages
- Sidebar: Role-aware navigation menu

## Best Practices Implemented

✅ **TypeScript Strict Mode** - Full type safety
✅ **Error Boundaries** - Graceful error handling
✅ **Loading States** - User feedback during async operations
✅ **Form Validation** - Zod schema validation
✅ **Security Headers** - Configured in next.config.js
✅ **Environment Variables** - Secure configuration
✅ **Code Splitting** - Automatic with Next.js
✅ **SEO Optimization** - Dynamic metadata
✅ **Responsive Design** - Mobile-first approach
✅ **Accessibility** - ARIA attributes and semantic HTML
✅ **Performance** - Image optimization, lazy loading
✅ **DRY Principle** - Reusable utilities and hooks

## Next Steps for Completion

1. **Create Additional Pages**
   - Member create/edit forms
   - Meeting create/edit with calendar
   - Activity management pages
   - Admin audit log viewer
   - Admin user management

2. **Implement Advanced Features**
   - QR code scanner for check-in
   - PDF generation for documents
   - Real-time notifications
   - Search and filtering enhancements
   - Data export (CSV/Excel)

3. **Testing**
   - Unit tests with Jest
   - Component tests with React Testing Library
   - Integration tests
   - E2E tests with Playwright

4. **Deployment**
   - CI/CD pipeline setup
   - Docker containerization
   - Cloud deployment (Vercel, AWS, etc.)
   - Performance monitoring

## Troubleshooting

### API Connection Issues
- Ensure backend is running on http://localhost:8000
- Check .env.local for correct API_URL
- Verify CORS headers in backend

### Token Issues
- Clear localStorage and login again
- Check browser console for auth errors
- Verify JWT token format in localStorage

### Styling Issues
- Ensure Tailwind CSS is properly configured
- Check tailwind.config.ts for custom theme
- Verify PostCSS configuration

## Performance Metrics

- **Lighthouse Score**: Target 90+
- **First Contentful Paint**: < 1.5s
- **Largest Contentful Paint**: < 2.5s
- **Cumulative Layout Shift**: < 0.1

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS Safari, Chrome Android)

## License

© 2024 National Association Management System (NANS)

## Support

For issues and feature requests, please contact the development team.
