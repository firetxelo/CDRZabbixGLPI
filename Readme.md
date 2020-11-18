# GLPI Zabbix Integration by python script

## By CDRTecnologia

### How To

1. pip install -r requirements.txt

1. Set the environment variables or change the values on the script

    1. GLPI_TOKEN = GLPI APP token on setup > General > API
    1. GLPI_URL = url.of.glpi.server/apirest.php
    1. GLPI_AUTH_TOKEN = User token on this format -> "user_token GLPIUSERTOKEN"
    1. GLPI_SOLUTION_ID = ID of a created type of ticket solution. When ticket is closed, the script use this solution type
    1. GLPI_ENTITIES_ID = Default entity when script open the ticket - root entity = 0
    1. ZabbixURL = Zabbix Server URL
    1. ZabbixUser = Zabbix User with rights to write on the problem
    1. ZabbixPass = Zabbix pass from user above

1. Create Zabbix Action to run the script

    1. Configuration > Action > New or edit an existing one
    1. In operations set type to remote command, check current host, choose custom script on type and execute on zabbix server.
In commands set the following:
        1. /path/to/python /path/to/CDRZabbixGLPI.py -a create -e {EVENT.ID} -n '{EVENT.NAME}' -o "{HOST.NAME}" -t {TRIGGER.ID}
    1. In recovery operations do the same but with the following command:
        1. /path/to/python /path/to/CDRZabbixGLPI.py -a finish -e {EVENT.ID}

        #### Hint: You can manage steps to delay the ticket creation.

#### Hint2: You can manage custom behaviors in Administration > Rules > Business Rules for tickets

