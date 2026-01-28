# Secrets Configuration

This directory contains sensitive configuration files for the CAE Platform.

## Files

- `postgres_password.txt` - PostgreSQL database password
- `flower_password.txt` - Flower monitoring dashboard password

## Setup Instructions

### 1. Generate PostgreSQL Password

```bash
openssl rand -base64 32 > secrets/postgres_password.txt
```

### 2. Generate Flower Password

```bash
openssl rand -base64 16 > secrets/flower_password.txt
```

### 3. Generate htpasswd for Nginx

```bash
# Install htpasswd tool if not available
# On Ubuntu/Debian: sudo apt-get install apache2-utils
# On macOS: brew install httpd

# Generate password file (replace 'admin' with your username)
htpasswd -bnC admin YOUR_PASSWORD > nginx/.htpasswd
```

### 4. Generate SSL Certificates (Optional, for HTTPS)

For production, use a valid SSL certificate from a CA (like Let's Encrypt).

For testing, you can generate self-signed certificates:

```bash
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout nginx/ssl/key.pem \
  -out nginx/ssl/cert.pem
```

### 5. Update Configuration

After generating secrets, update your `docker-compose.yml` to use environment variables:

```yaml
environment:
  - POSTGRES_PASSWORD_FILE=/run/secrets/postgres_password
  - FLOWER_PASSWORD_FILE=/run/secrets/flower_password
```

## Security Best Practices

1. **Never commit secrets to version control**
   - The `secrets/` directory should be in `.gitignore`
   - Use environment variables or secret management tools

2. **Use strong, random passwords**
   - Minimum 16 characters
   - Mix of uppercase, lowercase, numbers, and special characters

3. **Rotate passwords regularly**
   - Change passwords every 90 days
   - Update secrets files accordingly

4. **Limit access to secrets**
   - Set proper file permissions: `chmod 600 secrets/*`
   - Only grant access to authorized personnel

5. **Use secret management in production**
   - AWS Secrets Manager
   - Azure Key Vault
   - HashiCorp Vault
   - Kubernetes Secrets

## Environment Variables

For additional security, use environment variables instead of secrets files:

```bash
export POSTGRES_PASSWORD="your_secure_password"
export FLOWER_PASSWORD="your_secure_password"

docker-compose up -d
```

## Backup and Recovery

### Backup Secrets

```bash
# Create encrypted backup
tar -czf secrets-backup-$(date +%Y%m%d).tar.gz secrets/
gpg -c secrets-backup-$(date +%Y%m%d).tar.gz
rm secrets-backup-$(date +%Y%m%d).tar.gz
```

### Restore Secrets

```bash
# Decrypt and restore
gpg -d secrets-backup-YYYYMMDD.tar.gz.gpg | tar -xz
```

## Troubleshooting

### Secrets not found

```bash
# Verify secrets exist
ls -la secrets/

# Check file permissions
ls -l secrets/
```

### Docker can't read secrets

```bash
# Ensure files are readable by Docker
chmod 644 secrets/*
```

### Password authentication failed

```bash
# Regenerate the password
openssl rand -base64 32 > secrets/postgres_password.txt

# Restart services
docker-compose down
docker-compose up -d
```
