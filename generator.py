#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import socket
import logging
import os


def generate_templates(client_name, country_name, hostname, organization, days, verb, base_dir, ip):
  
  dir = '/etc/openvpn/clients/{}'.format(client_name)

  if not os.path.isdir(dir):
    os.makedirs(dir)
  
  commands = [
    "openssl genrsa -out /etc/openvpn/clients/{}/key.pem 2048".format(client_name),
    'openssl req -new -key /etc/openvpn/clients/{}/key.pem -out /etc/openvpn/clients/{}/csr.pem -subj "/C={}/emailAddress={}@{}/organizationName={}/CN={}"'.format(
      client_name, client_name,
      country_name, client_name, hostname, organization, client_name
    ),
    "openssl x509 -req -in /etc/openvpn/clients/{}/csr.pem -CA /etc/openvpn/ca.crt -CAkey /etc/openvpn/ca.key -CAcreateserial -out /etc/openvpn/clients/{}/crt.pem -days {}".format(
      client_name, client_name, days
    ),
  ]
  
  for cmd in commands:
    if os.system(cmd) != 0:
      raise Exception(cmd)
  
  
  with open('/etc/openvpn/ca.crt') as f:
    ca = f.read()
  
  with open('/etc/openvpn/ta.key') as f:
    tls = f.read()
  
  with open('/etc/openvpn/clients/{}/key.pem'.format(client_name)) as f:
    client_key = f.read()
  
  with open('/etc/openvpn/clients/{}/crt.pem'.format(client_name)) as f:
    client_crt = f.read()

  template_udp = '''client
dev tun
proto udp
sndbuf 0
rcvbuf 0
remote {} 5353
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
cipher AES-256-CBC
comp-lzo
key-direction 1
verb {}

<ca>
{}</ca>
<cert>
{}</cert>
<key>
{}</key>

<tls-auth>
{}</tls-auth>
'''.format(
    ip, verb,
    ca, client_crt, client_key, tls
  )

  template_tcp = '''client
dev tun
proto tcp
sndbuf 0
rcvbuf 0
remote {} 8443
resolv-retry infinite
nobind
persist-key
persist-tun
remote-cert-tls server
auth SHA512
cipher AES-256-CBC
comp-lzo
key-direction 1
verb {}

<ca>
{}</ca>
<cert>
{}</cert>
<key>
{}</key>

<tls-auth>
{}</tls-auth>
'''.format(
    ip, verb,
    ca, client_crt, client_key, tls
  )

  with open('/etc/openvpn/clients/{}_tcp.ovpn'.format(client_name), 'w+') as f:
    f.write(template_tcp)

  with open('/etc/openvpn/clients/{}_udp.ovpn'.format(client_name), 'w+') as f:
    f.write(template_udp)
  
  return {
    'name': client_name,
    'tcp': template_tcp,
    'udp': template_udp
  }




