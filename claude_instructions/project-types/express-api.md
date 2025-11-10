# Express API

Project-specific guidance for Express.js APIs.

---

## 🔍 Detection

Auto-detected when `package.json` contains `"express"` dependency.

---

## 🛠️ Commands

```bash
npm run dev          # Development with nodemon
npm test            # Run tests
npm run lint        # ESLint
npm run typecheck   # TypeScript checking
npm run build       # Build TypeScript
npm start           # Production
```

---

## 📁 Common Structure

```
project/
├── src/
│   ├── server.ts
│   ├── app.ts
│   ├── routes/
│   │   ├── index.ts
│   │   ├── users.ts
│   │   └── auth.ts
│   ├── controllers/
│   │   ├── userController.ts
│   │   └── authController.ts
│   ├── services/
│   │   └── userService.ts
│   ├── models/
│   │   └── User.ts
│   ├── middleware/
│   │   ├── auth.ts
│   │   ├── errorHandler.ts
│   │   └── validation.ts
│   └── utils/
│       └── logger.ts
├── tests/
├── dist/
└── package.json
```

---

## ⚙️ Express Patterns

### Basic Setup

```typescript
// src/app.ts
import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import { errorHandler } from './middleware/errorHandler';
import routes from './routes';

const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());

app.use('/api', routes);

app.use(errorHandler);

export default app;
```

### Routes

```typescript
// src/routes/users.ts
import { Router } from 'express';
import { authenticate } from '../middleware/auth';
import * as userController from '../controllers/userController';

const router = Router();

router.get('/', authenticate, userController.getUsers);
router.get('/:id', authenticate, userController.getUser);
router.post('/', userController.createUser);
router.put('/:id', authenticate, userController.updateUser);
router.delete('/:id', authenticate, userController.deleteUser);

export default router;
```

### Controllers

```typescript
// src/controllers/userController.ts
import { Request, Response, NextFunction } from 'express';
import * as userService from '../services/userService';

export async function getUsers(req: Request, res: Response, next: NextFunction) {
  try {
    const users = await userService.getAllUsers();
    res.json(users);
  } catch (error) {
    next(error);
  }
}

export async function createUser(req: Request, res: Response, next: NextFunction) {
  try {
    const user = await userService.createUser(req.body);
    res.status(201).json(user);
  } catch (error) {
    next(error);
  }
}
```

### Middleware

```typescript
// src/middleware/auth.ts
import jwt from 'jsonwebtoken';
import { Request, Response, NextFunction } from 'express';

export async function authenticate(req: Request, res: Response, next: NextFunction) {
  try {
    const token = req.headers.authorization?.replace('Bearer ', '');

    if (!token) {
      return res.status(401).json({ error: 'Authentication required' });
    }

    const decoded = jwt.verify(token, process.env.JWT_SECRET!);
    req.user = decoded;
    next();
  } catch (error) {
    res.status(401).json({ error: 'Invalid token' });
  }
}
```

### Error Handling

```typescript
// src/middleware/errorHandler.ts
import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

export function errorHandler(
  error: Error,
  req: Request,
  res: Response,
  next: NextFunction
) {
  logger.error('Request error', {
    error: error.message,
    stack: error.stack,
    path: req.path,
    method: req.method
  });

  if (error.name === 'ValidationError') {
    return res.status(400).json({ error: error.message });
  }

  if (error.name === 'UnauthorizedError') {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  res.status(500).json({ error: 'Internal server error' });
}
```

---

## 🧪 Testing

```typescript
// tests/users.test.ts
import request from 'supertest';
import app from '../src/app';

describe('GET /api/users', () => {
  it('returns 200 and users array', async () => {
    const response = await request(app)
      .get('/api/users')
      .set('Authorization', `Bearer ${validToken}`);

    expect(response.status).toBe(200);
    expect(Array.isArray(response.body)).toBe(true);
  });

  it('returns 401 without token', async () => {
    const response = await request(app).get('/api/users');
    expect(response.status).toBe(401);
  });
});
```

---

## 🔧 Environment Variables

```bash
# .env
NODE_ENV=development
PORT=3000
DATABASE_URL=postgresql://localhost/myapp
JWT_SECRET=your-secret-key
```

---

## ✅ Quality Gates

- [ ] All tests pass
- [ ] Linting passes
- [ ] TypeScript compiles
- [ ] All endpoints have authentication
- [ ] All inputs validated
- [ ] Error handling implemented
- [ ] Security middleware (helmet, cors) configured

---

## 🚀 Deployment

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY dist ./dist
CMD ["node", "dist/server.js"]
```

---

**Reference:** https://expressjs.com/
