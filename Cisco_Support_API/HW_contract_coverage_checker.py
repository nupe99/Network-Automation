from oauthlib.oauth2 import BackendApplicationClient
from requests.auth import HTTPBasicAuth
from requests_oauthlib import OAuth2Session
import time
import datetime as d
import requests


def list_to_string(the_list):
    new_string = ''
    for element in the_list:
        #determine if it's the first element. If so, add without comma
        if new_string == '':
            new_string = element
        #If it's the second element. Append to base string an add comm
        else:
            new_string = new_string + ',' + element
    return new_string


def make_api_call(client_id, client_secret, *serial_nums):

    #Set a few placeholders
    pid_list = []


    # Perform Oauth v2 and save token

    auth = HTTPBasicAuth(client_id, client_secret)
    client = BackendApplicationClient(client_id=client_id)
    oauth = OAuth2Session(client=client)
    token = oauth.fetch_token(token_url='https://cloudsso.cisco.com/as/token.oauth2', auth=auth)

    token = token['access_token']

    sn = list_to_string(serial_nums)


    smartnet_uri = f'https://api.cisco.com/sn2info/v2/coverage/summary/serial_numbers/{sn}'

    retries = 0

    while retries < 4:

        try:

            resp = requests.get(smartnet_uri, headers = {"Authorization":"Bearer " + token, "Accept":"application/json"}, timeout=60)

        except Exception as E:
            print("API Timeout....")
            print(E)
            retries +=1
            time.sleep(10)
            continue

        if resp.status_code != 200:
            print("something was wrong with API request")
            print(resp.status_code)
            retries +=1
            time.sleep(10)
            continue

        else:
            response = resp.json()
            for rec in response['serial_numbers']:
                inner_dic = {}
                customer = rec['contract_site_customer_name']
                city = rec['contract_site_city']
                state = rec['contract_site_state_province']
                is_covered = rec['is_covered']
                service_contract = rec['service_contract_number']
                service_level = rec['service_line_descr']
                coverage_end_date = rec['covered_product_line_end_date']
                sr_no = rec['sr_no']
                inner_dic = {"customer": customer, "city": city, "state": state, "is_covered": is_covered, "service_contract": service_contract, "service_level": service_level, "coverage_end_date": coverage_end_date, "sn": sr_no}
                pid_list.append(inner_dic)
        break
    else:
        print("API issue !!!! Reached max retries")
        sys.exit("")

    return pid_list


#Enter client ID and client secret for Oauth v2
client_id = '<client id>'
client_secret = '<client secret>'

#Add client ID, secret, and one or more serail numbers to check against API. Result is returned as a list of dictionary entries.
final_list = make_api_call(client_id, client_secret, 'serial_num1', 'serial_num2', 'serial_num3')
print(final_list)
