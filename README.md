**Loner** *(LOcal NamE Resolver)* is an easy to set up, locally bound DNS server that queries mutliple trusted remote DNS servers to find a concensus.

Loner takes no security precautions, and as such it is designed to be used over already encrypted and authenticated channels. Instead of focusing on built-in security, Loner emphasizes (relative) simplicity in the code and also a lot of comments, making it easier to audit and debug.

Right now it's only a skeleton, so use at your own risk.

One of our main goals is to make Loner as cross-platform as possible. Once Loner becomes (much) more polished, there will be easy-to-install executable binaries provided for every major platform.

**NOTE:** Loner requires Gevent 1.0 or later, which requires Python 2.7.5 or later to operate correctly. Older LTS releases of various Linux distros may only come with 2.7.4 or earlier.
