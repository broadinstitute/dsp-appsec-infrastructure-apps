# General Secure Coding Practices

This set of security guidelines is language/technology agnostic and it serves as a general secure coding practice. Implementation of these practices aims to help prevent most of the common software vulnerabilities and can be integrated into the software development lifecycle.

1. Verify Code
    * Use tested and approved managed code rather than creating new unmanaged code for common tasks
    * Use checksums or hashes to verify the integrity of interpreted code, libraries, executables, and configuration files
    * Review all secondary applications, third party code and libraries to determine business necessity and validate safe functionality, as these can introduce new vulnerabilities
2. Implement Least Privilege
    * In cases where the application must run with elevated privileges, raise privileges as late as possible, and drop them as soon as possible
    * Restrict users from generating new code or altering existing code
    * Utilize task specific built-in APIs to conduct operating system tasks. Do not allow the application to issue commands directly to the Operating System, especially through the use of application initiated command shells
3. Be Aware of Low-Level Errors
    * Do not pass user supplied data to any dynamic execution function
    * Avoid calculation errors by understanding your programming language's underlying representation and how it interacts with numeric calculation. Pay close attention to byte size discrepancies, precision, signed/unsigned distinctions, truncation, conversion and casting between types, "not-a-number" calculations, and how your language handles numbers that are too large or too small for its underlying representation
    * Utilize locking to prevent multiple simultaneous requests or use a synchronization mechanism to prevent race conditions
    * Protect shared variables and resources from inappropriate concurrent access