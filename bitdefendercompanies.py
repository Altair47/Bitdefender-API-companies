#! /usr/bin/env python3
# Authors: Sotirios Roussis (sroussis@space.gr), Nikolaos Petropoulos (https://github.com/Altair47)
# Version: 1.0.1
# python file.py api_key master_comp_id master_comp_name
# example: python '.\bitdefendercompanies.py' c15fa5cf48e879a54f945cbef45620a54c48b5bvzx987a754f5g4jdfbc5v5464 4g54564c5xc47s54f95a548f Master

import base64
import json
import sys

import requests


class BitDefenderAPI(object):

    def __init__(self, session, api_key):
        self.session = session

        self.headers = {
            'cookie': 'lang=en_US',
            'x-forwarded-for': '127.0.0.1',
            'content-type': 'application/json',
            'authorization': 'Basic {0}'.format(base64.b64encode((api_key + ':').encode('utf-8')).decode('utf-8')),
        }

    def bdget(self, url, params):
        return self.session.get(url, params=params, headers=self.headers)

    def bdpost(self, url, data):
        return self.session.post(url, headers=self.headers, data=data)


class BitDefenderNetwork(BitDefenderAPI):

    def __init__(self, session, api_key):
        BitDefenderAPI.__init__(self, session, api_key)
        self.url = 'https://cloudgz.gravityzone.bitdefender.com/api/v1.0/jsonrpc/network'

    def get_companies(self, company_id, company_name):
        data = {
            'method': 'getCompaniesList',
            'params': {
                'parentId': company_id,
            },
            'jsonrpc': '2.0',
            'id': -1,
        }

        response = self.bdpost(self.url, data=json.dumps(data))
        if not response.ok:
            return {}

        response = response.json()
        if not response:
            return {}

        response = response.get('result', [])
        if not response:
            return {}

        network_map = {
            company_id: {
                'name': company_name,
                'children': {},
            },
        }

        for sub_company in response:
            sub_company_id = sub_company.get('id')
            sub_company_name = sub_company.get('name')
            if not network_map[company_id]['children'].get(sub_company_id):
                network_map[company_id]['children'][sub_company_id] = {
                    'name': sub_company_name,
                    'children': {},
                }
                network_map[company_id]['children'][sub_company_id]['children'] = self.get_companies(sub_company_id, sub_company_name)
        
        return network_map

    def main(self, master_company_id, master_company_name):
        return json.dumps(self.get_companies(master_company_id, master_company_name))
        

if __name__ == '__main__':
    try:
        print(BitDefenderNetwork(requests.Session(), sys.argv[1]).main(sys.argv[2], sys.argv[3]))
    except IndexError:
        print('bitdefendercompanies.py "API Key" "Master Company ID" "Master Company Name"')
        sys.exit(1)
    except KeyboardInterrupt:
        print('Stopping')
        sys.exit(0)