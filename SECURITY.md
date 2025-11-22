# Security Policy

## Reporting Security Vulnerabilities

**Please DO NOT open public GitHub issues for security vulnerabilities.** Instead, please report them responsibly.

### Reporting Process

1. **Email**: Send a detailed report to sushrut.nistane@rysun.com with:
   - Description of the vulnerability
   - Steps to reproduce
   - Potential impact
   - Suggested fixes (if any)

2. **Include**:
   - Your contact information
   - Proposed timeline for disclosure
   - CVE details if available

3. **Response Timeline**:
   - Initial acknowledgment: 24-48 hours
   - Investigation and fix: 7-14 days
   - Public disclosure: Coordinated with reporter

## Security Best Practices

### Credentials & Secrets

- **NEVER commit secrets** to the repository:
  - API keys
  - Database credentials
  - Access tokens
  - Private keys

- **Always use `.env` files**:
  ```bash
  # Copy template
  cp .env.example .env
  # Edit with actual credentials
  # .env is in .gitignore - NEVER remove it
  ```

- **Use environment variables** in production:
  ```bash
  # Instead of hardcoding
  api_key = os.getenv("API_KEY")
  ```

- **Rotate credentials** if accidentally committed:
  - Revoke the exposed credential immediately
  - Use `git filter-branch` or `git-filter-repo` to remove from history
  - Force push with coordinator approval

### Code Security

- **Input Validation**:
  - Validate all user inputs
  - Use parameterized queries to prevent SQL injection
  - Sanitize outputs

- **Authentication**:
  - Use JWT tokens with short expiration
  - Implement rate limiting
  - Hash passwords with strong algorithms (bcrypt)

- **Authorization**:
  - Implement role-based access control (RBAC)
  - Check permissions on every protected endpoint
  - Log access attempts

- **Logging**:
  - Log security-relevant events
  - DO NOT log sensitive information
  - Keep logs for audit trails

### Dependency Management

- **Keep dependencies updated**:
  ```bash
  pip list --outdated
  npm outdated
  ```

- **Check for vulnerabilities**:
  ```bash
  pip-audit
  npm audit
  ```

- **Pin dependencies** in production

### Infrastructure Security

- **Docker**:
  - Use official base images
  - Don't run containers as root
  - Use read-only filesystems where possible
  - Scan images for vulnerabilities

- **Database**:
  - Use strong passwords
  - Enable SSL/TLS connections
  - Restrict network access
  - Regular backups

- **API**:
  - Use HTTPS only
  - Implement CORS properly
  - Use security headers
  - Validate all inputs

### Development Security

- **Git Practices**:
  - Sign commits with GPG
  - Use branch protection rules
  - Require code reviews
  - Don't commit to main directly

- **Environment Setup**:
  - Use separate dev/staging/prod environments
  - Never use production secrets in development
  - Regularly audit environment variables

## Security Headers

All production deployments should include:

```
Content-Security-Policy: default-src 'self'
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Third-Party Services

- **Pinecone**: API keys in .env, never in code
- **Anthropic**: Use API keys securely, implement rate limiting
- **MongoDB Atlas**: Use connection strings from environment
- **GitHub**: PAT tokens with minimal required scopes
- **Jenkins**: Credentials stored in Jenkins, not in repo

## Incident Response

If a security incident occurs:

1. **Contain**: Disable affected credentials
2. **Assess**: Determine scope and impact
3. **Notify**: Inform affected users if necessary
4. **Fix**: Patch the vulnerability
5. **Review**: Post-incident analysis

## Security Compliance

This project aims to comply with:
- OWASP Top 10
- CWE Top 25
- Industry security standards for AI/ML systems

## Security Acknowledgments

We appreciate responsible disclosure. Contributors who report vulnerabilities will be acknowledged (unless they prefer anonymity).

## Additional Resources

- [OWASP Security Cheat Sheet](https://cheatsheetseries.owasp.org/)
- [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security)
- [Python Security](https://python.readthedocs.io/en/stable/library/security_warnings.html)
