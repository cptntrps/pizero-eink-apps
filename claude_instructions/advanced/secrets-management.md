# Secrets Management

Secure handling of API keys, passwords, and sensitive configuration.

---

## 🚨 Critical Rules

- ✋ **NEVER commit secrets to git**
- ✋ **NEVER hardcode credentials in code**
- ✋ **NEVER log secrets**
- ✋ **NEVER expose secrets in client-side code**
- ✋ **ALWAYS use environment variables or secret managers**

---

## 🔐 Environment Variables

### Local Development

**.env file (NEVER commit):**
```bash
# .env (in .gitignore)
DATABASE_URL=postgresql://localhost/myapp_dev
API_KEY=sk_test_1234567890
JWT_SECRET=local_dev_secret_change_in_prod
STRIPE_SECRET_KEY=sk_test_abcdefg
```

**.env.example (committed):**
```bash
# .env.example (commit this)
DATABASE_URL=postgresql://localhost/myapp
API_KEY=your_api_key_here
JWT_SECRET=generate_random_secret
STRIPE_SECRET_KEY=your_stripe_key
```

**.gitignore:**
```
.env
.env.local
.env.*.local
*.pem
*.key
secrets/
```

---

### Loading Environment Variables

**Node.js:**
```javascript
import dotenv from 'dotenv';
dotenv.config();

const apiKey = process.env.API_KEY;
if (!apiKey) {
  throw new Error('API_KEY environment variable is required');
}
```

**Python:**
```python
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('API_KEY')
if not api_key:
    raise ValueError('API_KEY environment variable is required')
```

**Validation:**
```typescript
import { z } from 'zod';

const envSchema = z.object({
  DATABASE_URL: z.string().url(),
  API_KEY: z.string().min(1),
  JWT_SECRET: z.string().min(32),
  NODE_ENV: z.enum(['development', 'production', 'test']),
});

const env = envSchema.parse(process.env);
```

---

## ☁️ Production Secret Management

### AWS Secrets Manager

```typescript
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

const client = new SecretsManager({ region: 'us-east-1' });

async function getSecret(secretName: string) {
  const response = await client.getSecretValue({ SecretId: secretName });
  return JSON.parse(response.SecretString);
}

// Usage
const dbCredentials = await getSecret('prod/database');
const dbUrl = `postgresql://${dbCredentials.username}:${dbCredentials.password}@${dbCredentials.host}/${dbCredentials.database}`;
```

### Azure Key Vault

```typescript
import { SecretClient } from '@azure/keyvault-secrets';
import { DefaultAzureCredential } from '@azure/identity';

const client = new SecretClient(
  'https://myvault.vault.azure.net',
  new DefaultAzureCredential()
);

const secret = await client.getSecret('DatabasePassword');
console.log(secret.value);
```

### Google Secret Manager

```python
from google.cloud import secretmanager

client = secretmanager.SecretManagerServiceClient()
name = f"projects/{project_id}/secrets/{secret_id}/versions/latest"
response = client.access_secret_version(request={"name": name})
secret = response.payload.data.decode("UTF-8")
```

### HashiCorp Vault

```javascript
const vault = require('node-vault')({
  endpoint: 'http://localhost:8200',
  token: process.env.VAULT_TOKEN
});

const secret = await vault.read('secret/data/myapp/database');
const dbPassword = secret.data.data.password;
```

---

## 🔑 Secret Rotation

### Automatic Rotation Strategy

```
1. Generate new secret
2. Store new secret in secret manager
3. Update application config to use new secret
4. Grace period: Accept both old and new secret
5. After grace period: Invalidate old secret
```

**Example rotation workflow:**
```typescript
async function rotateApiKey() {
  // 1. Generate new key
  const newKey = generateSecureKey();

  // 2. Store in secret manager
  await secretsManager.putSecret('API_KEY_NEW', newKey);

  // 3. Update application (rolling deployment)
  //    App checks both API_KEY and API_KEY_NEW

  // 4. Wait 24 hours (grace period)
  await sleep(24 * 60 * 60 * 1000);

  // 5. Promote new key
  await secretsManager.putSecret('API_KEY', newKey);
  await secretsManager.deleteSecret('API_KEY_NEW');

  // 6. Invalidate old key at provider
  await apiProvider.revokeKey(oldKey);
}
```

---

## 🛡️ Secret Protection Patterns

### Never Log Secrets

```typescript
❌ Bad:
logger.info('User login', { email, password });
logger.debug('API request', { headers });

✅ Good:
logger.info('User login', { email });
logger.debug('API request', {
  headers: {
    ...headers,
    authorization: '[REDACTED]'
  }
});
```

### Redact Secrets in Errors

```typescript
function redactError(error: Error): Error {
  const message = error.message
    .replace(/api[_-]?key[\s:=]+[\w-]+/gi, 'api_key=[REDACTED]')
    .replace(/password[\s:=]+[\w-]+/gi, 'password=[REDACTED]')
    .replace(/token[\s:=]+[\w-]+/gi, 'token=[REDACTED]');

  return new Error(message);
}
```

### Secure Secret Comparison

```typescript
import crypto from 'crypto';

// Prevent timing attacks
function secureCompare(a: string, b: string): boolean {
  return crypto.timingSafeEqual(
    Buffer.from(a),
    Buffer.from(b)
  );
}
```

---

## 📦 Secrets in CI/CD

### GitHub Actions

```yaml
# .github/workflows/deploy.yml
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Deploy
        env:
          DATABASE_URL: ${{ secrets.DATABASE_URL }}
          API_KEY: ${{ secrets.API_KEY }}
        run: npm run deploy
```

**Setting secrets:** Repository Settings → Secrets and variables → Actions

### GitLab CI

```yaml
# .gitlab-ci.yml
deploy:
  script:
    - npm run deploy
  variables:
    DATABASE_URL: $CI_DATABASE_URL
    API_KEY: $CI_API_KEY
```

**Setting secrets:** Settings → CI/CD → Variables (mark as "protected" and "masked")

---

## 🔍 Secret Detection

### Pre-commit Hooks

```bash
# Install git-secrets
brew install git-secrets

# Setup
git secrets --install
git secrets --register-aws

# Scan
git secrets --scan
```

### GitHub Secret Scanning

Automatically enabled on public repos. For private repos: Settings → Code security and analysis → Enable secret scanning

### TruffleHog

```bash
# Scan git history
trufflehog git https://github.com/user/repo
```

---

## 📋 Secret Management Checklist

### Development
- [ ] All secrets in `.env` file
- [ ] `.env` in `.gitignore`
- [ ] `.env.example` provided
- [ ] No secrets in code
- [ ] Validation on startup

### Production
- [ ] Secrets in secret manager (AWS/Azure/GCP)
- [ ] Secrets not in environment variables (if using serverless)
- [ ] Secrets encrypted at rest
- [ ] Access logs enabled
- [ ] Rotation schedule defined

### Code Review
- [ ] No hardcoded secrets
- [ ] No secrets in logs
- [ ] No secrets in error messages
- [ ] No secrets in URLs
- [ ] Secrets compared securely

### Incident Response
- [ ] Rotation procedure documented
- [ ] Emergency rotation tested
- [ ] Secrets versioned
- [ ] Old secrets invalidated

---

## 🎯 Examples

### Example: API Key Management

**Bad:**
```typescript
// ❌ NEVER do this
const apiKey = 'sk_live_abcdefg1234567890';
fetch('https://api.example.com', {
  headers: { 'X-API-Key': apiKey }
});
```

**Good:**
```typescript
// ✅ Environment variable
const apiKey = process.env.API_KEY;
if (!apiKey) throw new Error('API_KEY not set');

fetch('https://api.example.com', {
  headers: { 'X-API-Key': apiKey }
});
```

**Better:**
```typescript
// ✅ Secret manager
import { getSecret } from './lib/secrets';

const apiKey = await getSecret('api-key');

fetch('https://api.example.com', {
  headers: { 'X-API-Key': apiKey }
});
```

---

### Example: Database Credentials

**Development:**
```bash
# .env
DATABASE_URL=postgresql://localhost/myapp_dev
```

**Production (AWS Secrets Manager):**
```typescript
const secrets = await getSecret('prod/database');

const pool = new Pool({
  host: secrets.host,
  port: secrets.port,
  database: secrets.database,
  user: secrets.username,
  password: secrets.password,
  ssl: { rejectUnauthorized: true }
});
```

---

**Remember:** Treat secrets like passwords - never share them, never write them down in public places, and rotate them regularly.
