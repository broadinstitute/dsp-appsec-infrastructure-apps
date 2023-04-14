security_headers = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'deny',
    'X-XSS-Protection': '1; mode=block',
    'Content-Security-Policy': 'default-src \'self\'',
    'Cache-Control': 'no-cache',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains'
}