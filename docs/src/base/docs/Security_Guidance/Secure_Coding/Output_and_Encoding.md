# Output & Encoding

1. Output Encoding Process
    * Conduct all encoding on a trusted system (e.g., The server)
    * Utilize a standard, tested routine for each type of outbound encoding
2. Encode Data
    * Contextually output encode all data returned to the client that originated outside the application's trust boundary. HTML entity encoding is one example, but does not work in all cases
    * Encode all characters unless they are known to be safe for the intended interpreter
3. Sanitize Output
    * Contextually sanitize all output of un-trusted data to queries for SQL, XML, and LDAP
    * Sanitize all output of un-trusted data to operating system commands

## Additional Advice for Securing Output

* Send X-Content-Type-Options: nosniff header.
* Send X-Frame-Options: deny header.
* Send Content-Security-Policy: default-src 'none' header.
* Remove fingerprinting headers - X-Powered-By, Server, X-AspNet-Version etc.
* Force content-type for your response, if you return application/json then your response content-type is application/json.
* Don't return sensitive data like credentials, Passwords, security tokens.
* Return the proper status code according to the operation completed (e.g. 200 OK, 400 Bad Request, 401 Unauthorized, 405 Method Not Allowed, etc.).