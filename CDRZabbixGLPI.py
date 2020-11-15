import os
import requests
import json
from pyzabbix import ZabbixAPI
import argparse
from datetime import datetime

GLPI_TOKEN = os.getenv('GLPI_APP_TOKEN')
GLPI_URL = os.getenv('GLPIURL', 'http://glpi.local/apirest.php')
GLPI_AUTH_TOKEN = os.getenv('GLPI_USER_AUTH_TOKEN', "user_token GLPIUSERTOKEN")
GLPI_SOLUTION_ID = 1
GLPI_ENTITIES_ID = 0
ZabbixURL = os.getenv('ZBXURL', 'http://localhost/zabbix')
ZabbixUser = os.getenv('ZBXUSER', 'Admin')
ZabbixPass = os.getenv('ZBXPASS', 'zabbix')

parser = argparse.ArgumentParser(description="Zabbix GLPI Integration by CDR Tecnologia")
parser.add_argument('-a',
                    '--action',
                    help="'create' to create a new ticket and 'finish' to finish a existing ticket",
                    default="create")
parser.add_argument('-e',
                    '--eventid',
                    help="inform macro {EVENT.ID} from zabbix server")
parser.add_argument('-n',
                    '--eventname',
                    help='inform macro {EVENT.NAME} from zabbix server')
parser.add_argument('-o',
                    '--hostname',
                    help='inform macro {HOST.NAME} from zabbix server')
parser.add_argument('-t',
                    '--triggerid',
                    help="inform macro {TRIGGER.ID} from zabbix server")
args = parser.parse_args()


def init_session():
    payload = {
        'Content-Type': 'application/json',
        'Authorization': GLPI_AUTH_TOKEN,
        'App-Token': GLPI_TOKEN
    }

    r = requests.get(GLPI_URL + '/initSession', headers=payload)
    res_dict = json.loads(r.text)
    return res_dict['session_token']


def kill_session(session_token):
    payload = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_TOKEN
    }
    r = requests.get(GLPI_URL + '/killSession', headers=payload)
    return r.text


def zbx_problem_severity(objectid):
    with ZabbixAPI(url=ZabbixURL, user=ZabbixUser, password=ZabbixPass) as zapi:
        problem = zapi.problem.get(objectids=objectid)

        return problem[0]['severity']


def create_ticket(eventid):
    session_token = (init_session())
    now = datetime.now()
    time = now.strftime("%Y-%m-%d %H:%M:%S")
    triggerid = args.triggerid
    hostname = args.hostname
    eventname = args.eventname
    severity = zbx_problem_severity(triggerid)
    header = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_TOKEN
    }
    data = {
        "input":
            [{"users_id": 4,
              "type": 1,
              "requesttypes_id": 6,
              "date": time,
              "date_mod": time,
              "date_creation": time,
              "entities_id": GLPI_ENTITIES_ID,
              "urgency": severity,
              "impact": severity,
              "priority": int(severity) + 1,
              "name": f"[ZBX-{eventid}] - {eventname} - {hostname}",
              "content": f"Ticket open by Zabbix Server\n Event: {eventname}\n Host: {hostname}"}]
    }
    r = requests.post(GLPI_URL + '/Ticket/', headers=header, data=json.dumps(data))
    kill_session(session_token)
    with ZabbixAPI(url=ZabbixURL, user=ZabbixUser, password=ZabbixPass) as zapi:
        zapi.event.acknowledge(eventids=eventid, action=6, message=f"Ticket ID on GLPÌ: {json.loads(r.text)[0]['id']}")
    return r.text


def search_ticket(zbxid):
    session_token = (init_session())
    header = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_TOKEN
    }
    r = requests.get(GLPI_URL + f'/search/Ticket?is_deleted=0&as_map=0&criteria[0][link]=AND&criteria[0]['
                                'field]=1&criteria[0][searchtype]=contains&criteria[0]['
                                f'value]=[ZBX-{zbxid}]&search=Pesquisar&itemtype=Ticket', headers=header, )
    kill_session(session_token)
    return json.loads(r.text)['data'][0]['2']


def update_ticket(zbxid):
    glpiid = search_ticket(zbxid)
    session_token = (init_session())
    header = {
        'Content-Type': 'application/json',
        'Session-Token': session_token,
        'App-Token': GLPI_TOKEN
    }
    data = {
        "input": [{
            "itemtype": "Ticket",
            "items_id": str(glpiid),
            "solutiontypes_id": GLPI_SOLUTION_ID,
            "status": 3,
            "content": "Problem Solved in Zabbix Server"
        }]
    }
    r = requests.post(GLPI_URL + '/itilsolution/', headers=header, data=json.dumps(data))
    kill_session(session_token)
    return r.text


if args.action == 'create':
    create_ticket(args.eventid)

if args.action == 'finish':
    update_ticket(args.eventid)
