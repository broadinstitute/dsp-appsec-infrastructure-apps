# Authentication

* Don't use Basic Auth. Use standard authentication (e.g. JWT, OAuth - use state param).
* Don't reinvent the wheel in Authentication, token generation password storage. Use the standards.
* Use Max Retry and jail features in Login.
* Use encryption on all sensitive data. 

## OAuth

* Always validate redirect_uri server-side to allow only whitelisted URLs.
* Always try to exchange for code and not tokens (don't allow response_type=token).
* Use state parameter with a random hash to prevent CSRF on the * OAuth authentication process.
* Define the default scope, and validate scope parameters for each application.

## JWT (JSON Web Token)

* Use a cryptographically secure random complicated key (JWT Secret) to make brute forcing the token very hard.
* Don't extract the algorithm from the payload. Force the algorithm in the backend (HS256 or RS256).
* Make token expiration (TTL, RTTL) as short as possible.
* Don't store sensitive data in the JWT payload, it can be decoded easily