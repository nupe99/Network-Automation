import requests
import json
import yaml
import yml2json
import time

lab_load_file = 'cml_lab_topology.yaml'

def get_token(creds_dic):

    try:

        creds = json.dumps(creds_dic)

        response = requests.post('https://10.10.20.161/api/v0/authenticate', creds, verify=False)

        token = response.json()

    except Exception as e:
        print("Failed to get token from devnet CML API")
        print(e)
        sys.exit("Stopping....")

    return token





def remove_devnet_labs(token):


    get_labs = 'https://10.10.20.161/api/v0/labs'

    resp = requests.get(get_labs, headers = {"Authorization":"Bearer " + token, "Accept":"application/json"}, timeout=20, verify=False)

    active_labs = resp.json()

    if active_labs:

        for active_lab in active_labs:
            stop_lab = f'https://10.10.20.161/api/v0/labs/{active_lab}/stop'
            wipe_lab = f'https://10.10.20.161/api/v0/labs/{active_lab}/wipe'
            delete_lab = f'https://10.10.20.161/api/v0/labs/{active_lab}'

            resp = requests.put(stop_lab, headers = {"Authorization":"Bearer " + token, "Accept":"application/json"},
                                timeout=60, verify=False)
            print(f' stopping existing labs - status code - {resp.status_code}')

            resp = requests.put(wipe_lab, headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                                timeout=60, verify=False)
            print(f' wiping exiting labs - status code - {resp.status_code}')

            resp = requests.delete(delete_lab, headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                                timeout=60, verify=False)

            print(f' deleting existing labs - status code - {resp.status_code}')

    else:

        print("no existing labs running. So nothing to Remove")


def build_lab(token, lab_name):

    #get CML topology build file
    f = open(lab_load_file, 'r')

    topology = f.read()

    f.close()


    build_uri = f'https://10.10.20.161/api/v0/import?title={lab_name}&is_json=false'


    response = requests.post(build_uri, headers = {"Authorization":"Bearer " + token, "Accept":"application/json"},
                             data=topology, timeout=60, verify=False)


    if response.status_code == 200:
        print("lab build was successful")
        response_dic = json.loads(response.content)
        new_lab = response_dic['id']
        start_lab = f'https://10.10.20.161/api/v0/labs/{new_lab}/start'
        resp = requests.put(start_lab, headers={"Authorization": "Bearer " + token, "Accept": "application/json"},
                            timeout=60, verify=False)
        print(f' starting new lab - status code - {resp.status_code}')
    else:
        print("A problem was encountered during the lab build")
        print(f'Status Code - {response.status_code}')
        print(response.content)

# Create dictionary with devnet CML sandbox creds
creds_dic = {'username': 'developer', 'password': 'C1sco12345'}

token = get_token(creds_dic)

#Remove existing lab topologies
remove_devnet_labs(token)

#Create new lab topology
build_lab(token, 'Test Lab')

