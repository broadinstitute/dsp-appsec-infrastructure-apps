# Docker Security on GCP

### Use Secure Images

1. Use the “secure” Docker base images.
   1.  [https://cloud.google.com/container-registry/docs/managed-base-images](https://cloud.google.com/container-registry/docs/managed-base-images)
2. Scan your images and respond to that regularly.
   1. [https://cloud.google.com/container-registry/docs/get-image-vulnerabilities](https://cloud.google.com/container-registry/docs/get-image-vulnerabilities)
   2. Feel free to put your images in any supported repository but ALSO put it in GCR to take advantage of this.

### **Appendix 1 - Create a VM instance using a CIS image**

1. In the GCP navigation menu select Compute Engine &gt; VM instances

2. Click on the ‘Create instance’ icon

![](https://lh4.googleusercontent.com/ny6bHkofYF-BMoV0g0gw-dk7ILahggoulCM4-XWdv211o7bnGjuAqm-jVr5xKOotw4NhvDgv2XOApwCtbKgUUtuosVaIzHcPmaAUpAqcxW2OWnXH0pKJpd1eAifgV_5IdnN06hXt)

3. Click on the Marketplace

![](https://lh6.googleusercontent.com/jdMC6JF3H87yegh8oDX-4fa4Mm3rg6Q9HLaa3PUBH-ph7fdcHBTeE7xCfXNDB9wl4OEqg8V1sAofx8Y5N4YytGeBRZ0Nz0XCTw2BYB3cbegsO4CcutFRV5d_Z-dArnBiYjrHAFp_)

4. Search for CIS in the Marketplace and select one of the CIS benchmark images  


![CIS images](https://lh6.googleusercontent.com/qyPh1WH4_tyum6lKX95V5_NpRsY0257QjLjpD-sStTc7m2St6Hyf2zD5S_eoQa4RyqBzhvXs2u5vOebA1IH0hHp838xLn_JGCwSDLqoR1ZRtram8ywcsekedH727eUDDzo9IQYPL)

