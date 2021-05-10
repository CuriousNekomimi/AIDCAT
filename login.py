import json
import urllib.request
import urllib.error
import getpass
import sys

loginpayload = {
	"variables": {
		"identifier": "",
		"email": "",
		"password": ""
	},
	"query": """
mutation ($identifier: String, $email: String, $password: String, $anonymousId: String) {
	login(identifier: $identifier, email: $email, password: $password, anonymousId: $anonymousId) {
		accessToken
	}
}
"""
}

loginpayload['variables']['identifier'] = loginpayload['variables']['email'] = input('Your username or e-mail: ')
loginpayload['variables']['password'] = getpass.getpass('Your password: ')
try:
	req = urllib.request.Request('https://api.aidungeon.io/graphql', headers={'content-type': 'application/json'})
	res = urllib.request.urlopen(req, data=json.dumps(loginpayload).encode('utf-8'))
	payload = json.load(res)
	if 'errors' in payload:
		print('Couldn\'t log in.')
		for error in payload['errors']:
			print(error['message'])
		sys.exit(1)
	elif 'data' in payload:
		print('Your access token is %s' % payload['data']['login']['accessToken'])
	else:
		print('no data?!')
		sys.exit(1)
except urllib.error.HTTPError as e:
	print(e)
	print(e.read())
	sys.exit(1)
