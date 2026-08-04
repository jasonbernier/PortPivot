# Port Pivot

**Port Pivot** is the research name assigned to an authenticated FTP
active-mode destination validation issue identified during a security
review of FileZilla Server.

The observed behavior allows an authenticated FTP client to specify
arbitrary destinations for active-mode (`PORT`/`EPRT`) data connections.
Under the tested conditions, the server subsequently initiated outbound
TCP connections to the supplied destination when a data-channel
operation was requested.

The finding was responsibly disclosed to the vendor and submitted to the
CVE Program before creation of this repository.

## Executive Summary

During manual source-code review and validation in a controlled
laboratory environment, active-mode FTP handling was observed accepting
client-specified destinations supplied through the PORT and EPRT
commands.

When a subsequent FTP data operation (such as LIST) was performed, the
FTP server initiated an outbound TCP connection to the specified
destination.

Depending on deployment configuration and network architecture, this
behavior may enable FTP bounce / SSRF-style interactions with systems
reachable from the FTP server.

## Vulnerability Classification

* CWE-918 -- Server-Side Request Forgery (SSRF)
* CWE-441 -- Unintended Proxy or Intermediary
* Historical classification: FTP Bounce Attack

## Potential Security Impact

* Outbound TCP connections from the FTP server
* Interaction with internal or localhost services
* SSRF-style network pivoting
* Firewall boundary bypass depending on deployment

## Recommended Mitigations

* Validate active-mode destinations.
* Restrict destinations to the authenticated control peer unless
third-party transfers are intentionally enabled.
* Add regression tests for PORT/EPRT handling.

## Advisory

### Summary

An authenticated user can influence the destination of FTP active-mode
data connections through the PORT and EPRT commands. Under the tested
conditions, the server initiated outbound TCP connections to
client-specified destinations after a data operation was requested.

### Tested Version

* FileZilla Server 1.12.6

## Responsible Disclosure

This repository will remain private until the coordinated disclosure
process concludes.

## Contact

Jason Bernier

Security Researcher

