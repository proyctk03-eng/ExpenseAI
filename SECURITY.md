# 🔐 Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ Yes     |
| < 1.0   | ❌ No      |

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please:
1. **DO NOT** disclose it publicly
2. Email us at: `[security@example.com]`
3. Provide as much information as possible

We will respond within 48 hours and work to resolve the issue promptly.

## Security Measures Implemented

- ✅ JWT authentication with short-lived access tokens via HttpOnly Cookies
- ✅ Refresh token mechanism for secure session management
- ✅ Password hashing using bcrypt
- ✅ SQL Injection prevention via SQLAlchemy ORM
- ✅ XSS protection through content escaping in Jinja2
- ✅ Rate limiting on authentication endpoints (SlowAPI)
- ✅ CORS configuration with strict origins
- ✅ Environment variables for sensitive data (API Keys)
- ✅ Dependency scanning for known vulnerabilities
