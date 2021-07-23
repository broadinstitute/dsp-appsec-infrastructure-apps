# Access Control

* Check if all the endpoints are protected behind authentication to avoid broken authentication process.
* User own resource ID should be avoided. Use /me/orders instead of /user/654321/orders.
* Don't auto-increment IDs. Use UUID instead.
* If you are parsing XML files, make sure entity parsing is not enabled to avoid XXE (XML external entity attack).
* If you are parsing XML files, make sure entity expansion is not enabled to avoid Billion Laughs/XML bomb via exponential entity expansion attack.
* Use a CDN for file uploads.
* If you are dealing with huge amount of data, use Workers and Queues to process as much as possible in background and return response fast to avoid HTTP Blocking.
* Do not forget to turn the DEBUG mode OFF.
* Limit requests (Throttling) to avoid DDoS / brute-force attacks.
* Use HTTPS on server side to avoid MITM (Man In The Middle Attack).
* Use HSTS header with SSL to avoid SSL Strip attack. 