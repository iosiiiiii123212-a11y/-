#!/usr/bin/env python3
"""
Generate self-signed SSL certificate for local development
"""
from OpenSSL import crypto
import os

def generate_self_signed_cert():
    # Create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, 2048)

    # Create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "IL"
    cert.get_subject().ST = "Israel"
    cert.get_subject().L = "Local"
    cert.get_subject().O = "WhatsApp Clone"
    cert.get_subject().OU = "Development"
    cert.get_subject().CN = "localhost"
    
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(365*24*60*60)  # Valid for 1 year
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha256')

    # Save certificate and private key
    with open("cert.pem", "wb") as f:
        f.write(crypto.dump_certificate(crypto.FILETYPE_PEM, cert))
    
    with open("key.pem", "wb") as f:
        f.write(crypto.dump_privatekey(crypto.FILETYPE_PEM, k))
    
    print("✅ Certificate generated successfully!")
    print("📁 Files created: cert.pem, key.pem")
    print("\n⚠️  Note: This is a self-signed certificate for development only.")
    print("Your browser will show a security warning - click 'Advanced' and 'Proceed'.")

if __name__ == "__main__":
    generate_self_signed_cert()
