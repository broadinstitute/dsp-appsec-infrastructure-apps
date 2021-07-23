# Threat Modeling

## Introduction

Threat modeling is an approach for analyzing the security of an application. It is a structured approach that enables you to identify, quantify, and address the security risks associated with an application.

**Threat Modeling Basics**

* **What?** 
  * A repeatable process to find and address all threats to your product  
* **Why?**  
  * Because attackers think differently
  * Find problems when there’s time to fix them 
  * Security Development Lifecycle(SDL) requirement 
  * Deliver more secure products 
* **When?** 
  * The earlier you start, the more time to plan and fix 
  * Worst case is for when you’re trying to ship: Find problems, make ugly scope and schedule choices, revisit those features soon

## Scope

While doing threat modeling/secure architecture review we can primarily focus on the following areas:

* [ ] Application Architecture Documents
* [ ] Deployment and Infrastructure Considerations
* [ ] Input Validation
* [ ] Authentication
* [ ] Authorization
* [ ] Configuration Management
* [ ] Session Management
* [ ] Cryptography(if applicable - hopefully not applicable 😅)  
* [ ] Parameter Manipulation
* [ ] Exception Management
* [ ] Auditing & Logging
* [ ] Application Framework and Libraries

## Threat Modeling Considerations

TODO

## Threat Modeling Tooling

Threat modeling can be assisted by tooling such as PyTM, in which Python code is used to model the system, and the PyTM library automatically generates diagrams and lists of dataflows and possible threats ready for human consideration.

## Threat Modeling Output

After the process of analyzing the assets, data flows, threats, and mitigations is complete, the result is a document

The output, a threat model, is a document(MS Word, HTML, etc.) that should be appropriately stored so that only stakeholders have access. The final Threat Model document must have a brief description of your product, Data Flow Diagram\(s) and the threats identified(following the structure described later in this Handbook). A complete threat model will include the following:

1. General and detailed Data Flow Diagrams(L0 and L1 DFDs)   
2. Network traffic requirements(ports in use, requirements from firewalls, etc.)   
3. Questions in the "Performing Threat Model" section have been answered.   
4. Findings the development team identified with ticket links(format specified below in the section, "Documenting Findings").   
5. In the Threat Model document, list:
6. Location and nature of sensitive data – the “crown jewels”(data, assets, functionality) that we want to protect.
7. Uses of cryptography.
8. The threat model Curator and other stakeholders involved.