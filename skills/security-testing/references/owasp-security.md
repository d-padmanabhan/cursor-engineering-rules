# OWASP Security Best Practices

**Goal:** Comprehensive security guide covering OWASP Top 10, secret management, vulnerability scanning, and secure coding practices.

## Guiding Principles

1. **Defense in Depth**: Multiple layers of security controls
2. **Least Privilege**: Minimum necessary permissions
3. **Fail Securely**: Errors should not expose sensitive information
4. **Security by Design**: Build security in from the start
5. **Zero Trust**: Never trust, always verify

---

## OWASP Top 10 (2021)

### A01: Broken Access Control

**Problem:** Users can access resources they shouldn't be able to access.

**Prevention:**

```typescript
// ❌ BAD - No authorization check
app.get('/api/users/:id', async (req, res) => {
  const user = await User.findById(req.params.id);
  res.json(user);
});

// ✅ GOOD - Verify user can access resource
app.get('/api/users/:id', authenticate, async (req, res) => {
  const requestedUserId = req.params.id;
  const currentUserId = req.user.id;

  // Users can only access their own data
  if (requestedUserId !== currentUserId && !req.user.isAdmin) {
    return res.status(403).json({ error: 'Forbidden' });
  }

  const user = await User.findById(requestedUserId);
  res.json(user);
});

// ⭐ EXCELLENT - Policy-based access control
import { authorize } from './policies';

app.get('/api/users/:id',
  authenticate,
  authorize('user', 'read'),
  async (req, res) => {
    const user = await User.findById(req.params.id);
    res.json(user);
  }
);
```

**Python Example:**

```python
from functools import wraps
from flask import abort, g

def require_same_user_or_admin(f):
    """Decorator to check if user can access resource."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id = kwargs.get('user_id')
        if g.current_user.id != user_id and not g.current_user.is_admin:
            abort(403, description="Forbidden")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/api/users/<user_id>')
@require_authentication
@require_same_user_or_admin
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())
```

---

### A02: Cryptographic Failures

**Problem:** Sensitive data exposed due to weak or missing encryption.

**Store Passwords Securely:**

```typescript
import bcrypt from 'bcrypt';

// ✅ GOOD - Hash passwords with bcrypt
async function hashPassword(password: string): Promise<string> {
  const saltRounds = 12;
  return await bcrypt.hash(password, saltRounds);
}

async function verifyPassword(password: string, hash: string): Promise<boolean> {
  return await bcrypt.compare(password, hash);
}

// ❌ BAD - Never store passwords in plain text
const user = { email: 'user@acme.com', password: 'secretPassword' };
```

**Encrypt Sensitive Data at Rest:**

```typescript
import crypto from 'crypto';

// Encrypt data
function encrypt(text: string, key: string): string {
  const iv = crypto.randomBytes(16);
  const cipher = crypto.createCipheriv('aes-256-gcm', Buffer.from(key, 'hex'), iv);

  let encrypted = cipher.update(text, 'utf8', 'hex');
  encrypted += cipher.final('hex');

  const authTag = cipher.getAuthTag();

  return iv.toString('hex') + ':' + authTag.toString('hex') + ':' + encrypted;
}

// Decrypt data
function decrypt(encryptedData: string, key: string): string {
  const [ivHex, authTagHex, encrypted] = encryptedData.split(':');

  const iv = Buffer.from(ivHex, 'hex');
  const authTag = Buffer.from(authTagHex, 'hex');
  const decipher = crypto.createDecipheriv('aes-256-gcm', Buffer.from(key, 'hex'), iv);

  decipher.setAuthTag(authTag);

  let decrypted = decipher.update(encrypted, 'hex', 'utf8');
  decrypted += decipher.final('utf8');

  return decrypted;
}
```

**Use HTTPS Everywhere:**

```typescript
// ✅ GOOD - Force HTTPS
import helmet from 'helmet';
import express from 'express';

const app = express();
app.use(helmet.hsts({
  maxAge: 31536000,
  includeSubDomains: true,
  preload: true
}));
```

---

### A03: Injection

**Problem:** Untrusted data sent to interpreter as part of command or query.

**SQL Injection Prevention:**

```typescript
// ❌ BAD - SQL injection vulnerability
app.get('/api/users', async (req, res) => {
  const name = req.query.name;
  const query = `SELECT * FROM users WHERE name = '${name}'`;
  const users = await db.query(query);
  res.json(users);
});

// ✅ GOOD - Parameterized queries
app.get('/api/users', async (req, res) => {
  const name = req.query.name;
  const users = await db.query(
    'SELECT * FROM users WHERE name = $1',
    [name]
  );
  res.json(users);
});

// ⭐ EXCELLENT - ORM with type safety
import { User } from './models';

app.get('/api/users', async (req, res) => {
  const name = req.query.name;
  const users = await User.findAll({
    where: { name }
  });
  res.json(users);
});
```

**Python SQL Injection Prevention:**

```python
import psycopg2

# ❌ BAD - SQL injection vulnerability
def get_user_by_name(name: str):
    query = f"SELECT * FROM users WHERE name = '{name}'"
    cursor.execute(query)
    return cursor.fetchall()

# ✅ GOOD - Parameterized queries
def get_user_by_name(name: str):
    query = "SELECT * FROM users WHERE name = %s"
    cursor.execute(query, (name,))
    return cursor.fetchall()

# ⭐ EXCELLENT - ORM
from sqlalchemy.orm import Session
from models import User

def get_user_by_name(session: Session, name: str):
    return session.query(User).filter(User.name == name).all()
```

**Command Injection Prevention:**

```typescript
// ❌ BAD - Command injection vulnerability
import { exec } from 'child_process';

app.post('/api/ping', (req, res) => {
  const host = req.body.host;
  exec(`ping -c 4 ${host}`, (error, stdout) => {
    res.send(stdout);
  });
});

// ✅ GOOD - Input validation and safe execution
import { spawn } from 'child_process';

app.post('/api/ping', (req, res) => {
  const host = req.body.host;

  // Validate input
  if (!/^[a-zA-Z0-9.-]+$/.test(host)) {
    return res.status(400).json({ error: 'Invalid host' });
  }

  // Use spawn with separate arguments (no shell interpretation)
  const ping = spawn('ping', ['-c', '4', host]);

  let output = '';
  ping.stdout.on('data', (data) => {
    output += data.toString();
  });

  ping.on('close', (code) => {
    res.json({ output, code });
  });
});
```

---

### A04: Insecure Design

**Problem:** Missing or ineffective security controls by design.

**Rate Limiting:**

```typescript
import rateLimit from 'express-rate-limit';

// ✅ GOOD - Rate limiting to prevent brute force
const loginLimiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 5, // Limit each IP to 5 requests per windowMs
  message: 'Too many login attempts, please try again later',
  standardHeaders: true,
  legacyHeaders: false,
});

app.post('/api/login', loginLimiter, async (req, res) => {
  // Login logic
});

// ✅ GOOD - Global rate limiting
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
});

app.use('/api/', globalLimiter);
```

**Input Validation:**

```typescript
import { z } from 'zod';

// ⭐ EXCELLENT - Schema validation with Zod
const UserSchema = z.object({
  email: z.string().email().max(255),
  password: z.string().min(8).max(128)
    .regex(/[A-Z]/, 'Must contain uppercase letter')
    .regex(/[a-z]/, 'Must contain lowercase letter')
    .regex(/[0-9]/, 'Must contain number')
    .regex(/[^A-Za-z0-9]/, 'Must contain special character'),
  name: z.string().min(1).max(100),
});

app.post('/api/users', async (req, res) => {
  try {
    const validatedData = UserSchema.parse(req.body);
    const user = await createUser(validatedData);
    res.json(user);
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ errors: error.errors });
    }
    throw error;
  }
});
```

---

### A05: Security Misconfiguration

**Problem:** Insecure default configurations, incomplete configurations, open cloud storage.

**Security Headers:**

```typescript
import helmet from 'helmet';

app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", 'data:', 'https:'],
      connectSrc: ["'self'"],
      fontSrc: ["'self'"],
      objectSrc: ["'none'"],
      mediaSrc: ["'self'"],
      frameSrc: ["'none'"],
    },
  },
  hsts: {
    maxAge: 31536000,
    includeSubDomains: true,
    preload: true,
  },
  noSniff: true,
  xssFilter: true,
  referrerPolicy: { policy: 'strict-origin-when-cross-origin' },
}));

// ✅ GOOD - CORS configuration
import cors from 'cors';

app.use(cors({
  origin: ['https://acme.com', 'https://www.acme.com'],
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE'],
  allowedHeaders: ['Content-Type', 'Authorization'],
}));
```

**Disable Debug Mode in Production:**

```typescript
// ✅ GOOD - Environment-based configuration
const app = express();

if (process.env.NODE_ENV === 'production') {
  app.set('trust proxy', 1);
  app.use(express.static('public', { maxAge: '1y' }));
} else {
  // Development-only middleware
  app.use(morgan('dev'));
}

// ❌ BAD - Debug mode in production
app.use((err, req, res, next) => {
  res.status(500).json({
    error: err.message,
    stack: err.stack, // Exposes stack trace
  });
});

// ✅ GOOD - Safe error handling
app.use((err, req, res, next) => {
  console.error(err.stack);

  if (process.env.NODE_ENV === 'production') {
    res.status(500).json({ error: 'Internal server error' });
  } else {
    res.status(500).json({
      error: err.message,
      stack: err.stack,
    });
  }
});
```

---

### A06: Vulnerable and Outdated Components

**Problem:** Using components with known vulnerabilities.

**Regular Dependency Updates:**

```bash
# Check for vulnerabilities
npm audit
npm audit fix

# Use automated tools
npx npm-check-updates -u
npm install

# Dependabot (GitHub) - .github/dependabot.yml
version: 2
updates:
  - package-ecosystem: "npm"
    directory: "/"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10
```

**Lock File Scanning:**

```yaml
# GitHub Actions - Vulnerability scanning
name: Security Scan

on: [push, pull_request]

jobs:
  scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run npm audit
        run: npm audit --audit-level=high

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'
```

---

### A07: Identification and Authentication Failures

**Problem:** Weak authentication, session management issues.

**Strong Password Requirements:**

```typescript
import { z } from 'zod';

const passwordSchema = z.string()
  .min(12, 'Password must be at least 12 characters')
  .max(128, 'Password must be less than 128 characters')
  .regex(/[A-Z]/, 'Must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Must contain at least one special character');

function validatePassword(password: string): boolean {
  return passwordSchema.safeParse(password).success;
}
```

**Secure Session Management:**

```typescript
import session from 'express-session';
import RedisStore from 'connect-redis';
import { createClient } from 'redis';

// ✅ GOOD - Secure session configuration
const redisClient = createClient({ url: process.env.REDIS_URL });
const redisStore = new RedisStore({ client: redisClient });

app.use(session({
  store: redisStore,
  secret: process.env.SESSION_SECRET!,
  resave: false,
  saveUninitialized: false,
  name: 'sessionId', // Don't use default 'connect.sid'
  cookie: {
    secure: process.env.NODE_ENV === 'production', // HTTPS only
    httpOnly: true, // Prevent XSS
    maxAge: 1000 * 60 * 60 * 24, // 24 hours
    sameSite: 'strict', // CSRF protection
  },
}));
```

**Multi-Factor Authentication:**

```typescript
import speakeasy from 'speakeasy';

// Generate TOTP secret
function generateTOTPSecret(email: string) {
  const secret = speakeasy.generateSecret({
    name: `Acme (${email})`,
    issuer: 'Acme',
  });

  return {
    secret: secret.base32,
    qrCode: secret.otpauth_url,
  };
}

// Verify TOTP token
function verifyTOTP(secret: string, token: string): boolean {
  return speakeasy.totp.verify({
    secret,
    encoding: 'base32',
    token,
    window: 2, // Allow 2 time steps
  });
}
```

---

### A08: Software and Data Integrity Failures

**Problem:** Code and infrastructure that does not protect against integrity violations.

**Verify Package Integrity:**

```bash
# Use package lock files
npm ci  # Install exact versions from package-lock.json

# Verify package signatures
npm install --ignore-scripts  # Prevent post-install scripts

# Use Subresource Integrity (SRI) for CDN resources
<script
  src="https://cdn.jsdelivr.net/npm/vue@3/dist/vue.global.js"
  integrity="sha384-..."
  crossorigin="anonymous">
</script>
```

**Sign Releases:**

```bash
# Sign Docker images with Cosign
cosign sign --key cosign.key acme.com/app:v1.0.0

# Verify signature
cosign verify --key cosign.pub acme.com/app:v1.0.0

# Sign Git commits and tags
git config user.signingkey YOUR_GPG_KEY
git config commit.gpgsign true
git config tag.gpgsign true
```

---

### A09: Security Logging and Monitoring Failures

**Problem:** Insufficient logging and monitoring, inadequate response to incidents.

**Comprehensive Logging:**

```typescript
import winston from 'winston';

// ✅ GOOD - Structured logging
const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { service: 'api' },
  transports: [
    new winston.transports.File({ filename: 'error.log', level: 'error' }),
    new winston.transports.File({ filename: 'combined.log' }),
  ],
});

// Log security events
function logSecurityEvent(event: string, details: Record<string, unknown>) {
  logger.warn('Security event', {
    event,
    ...details,
    timestamp: new Date().toISOString(),
  });
}

// Authentication attempts
app.post('/api/login', async (req, res) => {
  const { email, password } = req.body;
  const user = await User.findOne({ email });

  if (!user || !(await user.verifyPassword(password))) {
    logSecurityEvent('failed_login', {
      email,
      ip: req.ip,
      userAgent: req.headers['user-agent'],
    });
    return res.status(401).json({ error: 'Invalid credentials' });
  }

  logSecurityEvent('successful_login', {
    userId: user.id,
    email,
    ip: req.ip,
  });

  res.json({ token: generateToken(user) });
});
```

**Monitor for Suspicious Activity:**

```typescript
// Track failed login attempts
const failedAttempts = new Map<string, number>();

function trackFailedLogin(email: string): boolean {
  const attempts = (failedAttempts.get(email) || 0) + 1;
  failedAttempts.set(email, attempts);

  // Lock account after 5 failed attempts
  if (attempts >= 5) {
    logger.warn('Account locked due to failed login attempts', {
      email,
      attempts,
    });
    return true;
  }

  return false;
}
```

---

### A10: Server-Side Request Forgery (SSRF)

**Problem:** Application fetches remote resource without validating user-supplied URL.

**Prevention:**

```typescript
import { URL } from 'url';

// ❌ BAD - SSRF vulnerability
app.post('/api/fetch', async (req, res) => {
  const url = req.body.url;
  const response = await fetch(url);
  const data = await response.text();
  res.send(data);
});

// ✅ GOOD - Validate and restrict URLs
const ALLOWED_DOMAINS = ['api.acme.com', 'cdn.acme.com'];
const BLOCKED_IPS = ['127.0.0.1', '0.0.0.0', '169.254.169.254'];

function isUrlSafe(urlString: string): boolean {
  try {
    const url = new URL(urlString);

    // Only allow HTTP/HTTPS
    if (!['http:', 'https:'].includes(url.protocol)) {
      return false;
    }

    // Check against allowlist
    if (!ALLOWED_DOMAINS.includes(url.hostname)) {
      return false;
    }

    // Block private IP ranges
    if (
      url.hostname === 'localhost' ||
      url.hostname.startsWith('192.168.') ||
      url.hostname.startsWith('10.') ||
      BLOCKED_IPS.includes(url.hostname)
    ) {
      return false;
    }

    return true;
  } catch {
    return false;
  }
}

app.post('/api/fetch', async (req, res) => {
  const url = req.body.url;

  if (!isUrlSafe(url)) {
    return res.status(400).json({ error: 'Invalid URL' });
  }

  try {
    const response = await fetch(url, {
      signal: AbortSignal.timeout(5000),
      redirect: 'manual',
    });

    const data = await response.text();
    res.send(data);
  } catch (error) {
    logger.error('Fetch error', { url, error });
    res.status(500).json({ error: 'Failed to fetch resource' });
  }
});
```

---

## Secret Management

### Environment Variables

```bash
# .env (NEVER commit this file)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JWT_SECRET=your-secret-key-here
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY

# .env.example (Commit this)
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
JWT_SECRET=generate-a-strong-secret
AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
```

### AWS Secrets Manager

```typescript
import { SecretsManagerClient, GetSecretValueCommand } from '@aws-sdk/client-secrets-manager';

async function getSecret(secretName: string): Promise<string> {
  const client = new SecretsManagerClient({ region: 'us-east-1' });

  try {
    const response = await client.send(
      new GetSecretValueCommand({ SecretId: secretName })
    );

    return response.SecretString!;
  } catch (error) {
    console.error('Failed to retrieve secret', { secretName, error });
    throw error;
  }
}

// Usage
const dbPassword = await getSecret('prod/database/password');
```

### HashiCorp Vault

```typescript
import vault from 'node-vault';

const client = vault({
  endpoint: process.env.VAULT_ADDR,
  token: process.env.VAULT_TOKEN,
});

async function getSecret(path: string): Promise<Record<string, unknown>> {
  try {
    const result = await client.read(path);
    return result.data;
  } catch (error) {
    console.error('Failed to retrieve secret from Vault', { path, error });
    throw error;
  }
}

// Usage
const secrets = await getSecret('secret/data/myapp/prod');
const dbPassword = secrets.password;
```

---

## Security Scanning Tools

### Pre-Commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/trufflesecurity/trufflehog
    rev: v3.63.0
    hooks:
      - id: trufflehog
        name: TruffleHog
        entry: trufflehog filesystem --no-update
        language: system

  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.4.0
    hooks:
      - id: detect-secrets
        name: Detect Secrets

  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.1
    hooks:
      - id: gitleaks
```

### CI/CD Security Scanning

```yaml
# .github/workflows/security.yml
name: Security Scan

on: [push, pull_request]

jobs:
  security:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run Trivy
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: '.'
          format: 'sarif'
          output: 'trivy-results.sarif'

      - name: Run Snyk
        uses: snyk/actions/node@master
        env:
          SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}

      - name: Run Bandit (Python)
        run: |
          pip install bandit
          bandit -r . -f json -o bandit-report.json
```

---

## Security Checklist

### Code Review Checklist

- [ ] No hardcoded secrets (API keys, passwords, tokens)
- [ ] Input validation on all user inputs
- [ ] Parameterized queries (no SQL injection)
- [ ] Output encoding (prevent XSS)
- [ ] Authentication required for protected routes
- [ ] Authorization checks for resource access
- [ ] Rate limiting on sensitive endpoints
- [ ] HTTPS enforced
- [ ] Security headers configured
- [ ] Error messages don't leak sensitive info
- [ ] Logging includes security events
- [ ] Dependencies are up to date
- [ ] Secrets stored in secret manager (not env vars in production)

### Deployment Checklist

- [ ] Debug mode disabled in production
- [ ] HTTPS configured with valid certificate
- [ ] Security headers configured (CSP, HSTS, etc.)
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Monitoring and alerting configured
- [ ] Backups configured and tested
- [ ] Incident response plan documented
- [ ] Security scanning in CI/CD pipeline
- [ ] Secrets rotated regularly
- [ ] Least privilege IAM roles/policies
- [ ] Network security groups configured
