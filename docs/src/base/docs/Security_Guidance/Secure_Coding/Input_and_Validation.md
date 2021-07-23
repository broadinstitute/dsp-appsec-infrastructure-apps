# Input & Validation

1. Processing Data
    * Specify proper character sets, such as UTF-8, for all sources of input
    * Verify that header values in both requests and responses contain only ASCII characters
    * Encode data to a common character set before validating (Canonicalize)
    * Determine if the system supports UTF-8 extended character sets and if so, validate after UTF-8 decoding is completed
2. Where to Validate
    * Identify all data sources and classify them into trusted and untrusted. Validate all data from untrusted sources (e.g., Databases, file streams, etc.)
    * Conduct all data validation on a trusted system (e.g., The server)
    * There should be a centralized input validation routine for the application
3. When to Validate
    * Validate all client provided data before processing, including all parameters, URLs and HTTP header content (e.g. Cookie names and values). Be sure to include automated post backs from JavaScript, Flash or other embedded code
    * Validate data from redirects (An attacker may submit malicious content directly to the target of the redirect, thus circumventing application logic and any validation performed before the redirect)
4. What to Validate
    * Validate for expected data types
    * Validate data range
    * Validate data length
    * Validate all input against a "white" list of allowed characters, whenever possible
    * If any potentially hazardous characters must be allowed as input, be sure that you implement additional controls like output encoding, secure task specific APIs and accounting for the utilization of that data throughout the application. Examples of common hazardous characters include: `&lt; &gt; " ' %( ) & + ' "`

## Additional Advice for Securing Input

* Use the proper HTTP method according to the operation: GET (read), POST (create), PUT/PATCH (replace/update), and DELETE (to delete a record), and respond with 405 Method Not Allowed if the requested method isn't appropriate for the requested resource.
* Validate content-type on request Accept header (Content Negotiation) to allow only your supported format (e.g. application/xml, application/json, etc) and respond with 406 Not Acceptable response if not matched.
* Validate content-type of posted data as you accept (e.g. application/x-www-form-urlencoded, multipart/form-data, application/json, etc).
* Validate User input to avoid common vulnerabilities (e.g. XSS, SQL-Injection, Remote Code Execution, etc).
* Don't use any sensitive data (credentials, Passwords, security tokens, or API keys) in the URL, but use standard Authorization header.
* Use an API Gateway service to enable caching, Rate Limit policies (e.g. Quota, Spike Arrest, Concurrent Rate Limit) and deploy APIs resources dynamically.