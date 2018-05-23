import requests


def create_ovpn_client_configuration(client_name):
  url = 'http://127.0.0.1:8080/generate/openvpn/{}/'.format(client_name)
  params = {
    'country_name': 'RU',
    'hostname': 'vpn.local',
    'organization': 'BeerVPN',
    'days': 365,
    'verb': 30
  }
  r = requests.get(url, params=params).json()
  return r['status']

def get_ovpn_client_configuration(client_name):
  url = 'http://127.0.0.1:8080/get/openvpn/{}/'.format(client_name)
  r = requests.get(url).json()
  if not r['status']:
    raise Exception('API failure. Please, see logs.')
  r.pop('status')
  return r



def ensure_client_created(clients):
  for client in clients:
    if create_ovpn_client_configuration(client):
      r = get_ovpn_client_configuration(client)
      print(
        r['tcp']
      )
      print(
        r['udp']
      )

