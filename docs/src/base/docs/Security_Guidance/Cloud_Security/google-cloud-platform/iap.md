# IAP

Consider using [Cloud IAP](https://cloud.google.com/iap)(Identity-Aware Proxy) to enable authentication for your backend services(GCE, GKE, AppEngine, or [on-premises apps](https://cloud.google.com/iap/docs/cloud-iap-for-on-prem-apps-overview)). This service provides:

* a seamless way to authenticate users to your web service with [Google IAM](https://cloud.google.com/iap/docs/concepts-overview) or an [external identity](https://cloud.google.com/iap/docs/external-identities)
* a way to connect over [TCP forwarding](https://cloud.google.com/iap/docs/tcp-forwarding-overview) to your private GCE instances without public IPs
  * this includes, but is not limited to SSH connections

Please note there are several ways to set up web authentication:

* [Cookie-based](https://cloud.google.com/iap/docs/sessions-howto) authentication, which enables web user login without writing any client code
* Programmatic authentication using [FirebaseUI](https://cloud.google.com/iap/docs/using-firebaseui) client library, which takes care of all of the low-level details and provides a user ID token to be sent to your service using `Authorization: Bearer` scheme
* Programmatic authentication with a [Service Account](https://cloud.google.com/iap/docs/authentication-howto#authenticating_from_a_service_account)(for service-to-service authentication), also using `Authorization: Bearer` token scheme

Please note that _cookie-based_ mechanism is currently vulnerable to **Cross-Site Request Forgery**(**CSRF**) attacks(due to its `SameSite=None` cookie setting), so you still need to implement a [proper method of protection](https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html) against it in your web app. Please consult with [AppSec team](mailto:appsec@broadinstitute.org) for details.

Due to this concern, we recommend using _programmatic authentication_ where possible.

Additionally, please note that beyond configuring IAP on the client side, Google recommends to validate user JWT tokens that IAP sends to your backend(for all mechanisms of client authentication). Please follow [this guide](https://cloud.google.com/iap/docs/signed-headers-howto) for details.

