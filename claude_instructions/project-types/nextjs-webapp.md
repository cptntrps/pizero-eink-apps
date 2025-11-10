# Next.js Web Application

Project-specific guidance for Next.js applications.

---

## 🔍 Detection

Auto-detected when these files exist:
- `next.config.js` or `next.config.ts`
- `package.json` with `"next"` dependency

---

## 🛠️ Commands

```bash
# Development
npm run dev

# Testing
npm test
npm run test:watch

# Linting
npm run lint
npm run lint -- --fix

# Type checking
npm run type-check
# or
npx tsc --noEmit

# Build
npm run build

# Production
npm start
```

---

## 📁 Common Structure

```
project/
├── app/                    # App Router (Next.js 13+)
│   ├── page.tsx
│   ├── layout.tsx
│   └── api/
│       └── route.ts
├── pages/                  # Pages Router (legacy)
│   ├── index.tsx
│   ├── _app.tsx
│   └── api/
│       └── endpoint.ts
├── components/
│   ├── ui/
│   └── features/
├── lib/
│   ├── utils.ts
│   └── api.ts
├── public/
│   └── images/
├── styles/
│   └── globals.css
└── tests/
    ├── unit/
    └── integration/
```

---

## ⚙️ Next.js Patterns

### API Routes (App Router)

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const users = await db.users.findAll();
    return NextResponse.json(users);
  } catch (error) {
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  const body = await request.json();
  // Handle POST
}
```

### Server Components (Default)

```tsx
// app/users/page.tsx
async function UsersPage() {
  // Fetch data directly in server component
  const users = await db.users.findAll();

  return (
    <div>
      {users.map(user => (
        <UserCard key={user.id} user={user} />
      ))}
    </div>
  );
}

export default UsersPage;
```

### Client Components

```tsx
'use client';

import { useState } from 'react';

export function Counter() {
  const [count, setCount] = useState(0);

  return (
    <button onClick={() => setCount(count + 1)}>
      Count: {count}
    </button>
  );
}
```

---

## 🧪 Testing Patterns

```typescript
// components/Button.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { Button } from './Button';

describe('Button', () => {
  it('renders with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  it('calls onClick when clicked', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click</Button>);

    fireEvent.click(screen.getByText('Click'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });
});
```

---

## 🔧 Environment Variables

```bash
# .env.local (not committed)
DATABASE_URL=postgresql://localhost/myapp
NEXT_PUBLIC_API_URL=http://localhost:3000/api

# .env.example (committed)
DATABASE_URL=your_database_url
NEXT_PUBLIC_API_URL=your_api_url
```

**Note:** Variables prefixed with `NEXT_PUBLIC_` are exposed to the browser.

---

## 📦 Common Dependencies

```json
{
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.0.0",
    "react-dom": "^18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "@types/react": "^18.0.0",
    "typescript": "^5.0.0",
    "eslint": "^8.0.0",
    "eslint-config-next": "^14.0.0"
  }
}
```

---

## ✅ Quality Gates

- [ ] `npm run lint` passes
- [ ] `npm run type-check` passes (or `tsc --noEmit`)
- [ ] `npm test` passes
- [ ] `npm run build` succeeds
- [ ] No `console.log` in production code
- [ ] Environment variables documented in `.env.example`

---

## 🚀 Deployment

**Vercel (Recommended):**
```bash
npm install -g vercel
vercel
```

**Docker:**
```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build
CMD ["npm", "start"]
```

**Build Output:**
```bash
npm run build
# Creates .next/ directory
npm start  # Production server
```

---

## 💡 Next.js-Specific Best Practices

1. **Use Server Components by default** - Only use `'use client'` when needed
2. **Fetch data in Server Components** - No need for useEffect
3. **Optimize images** - Use `next/image` component
4. **Use App Router** - Preferred over Pages Router (Next.js 13+)
5. **Handle loading/error states** - Use `loading.tsx` and `error.tsx`
6. **Implement proper metadata** - SEO with `metadata` export

---

**Reference:** https://nextjs.org/docs
