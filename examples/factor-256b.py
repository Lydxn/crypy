"""
Example of factoring a 256-bit semiprime using CADO-NFS.
"""
from Crypto.Util.number import getPrime
from crypy import factor_cado

def main():
    p = getPrime(128)
    q = getPrime(128)
    n = p * q
    print('got:', factor_cado(n))
    print('expected:', (p, q))

if __name__ == '__main__':
    main()