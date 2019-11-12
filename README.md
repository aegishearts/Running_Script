# API/SSH handling script
This repository include follow function to support other automation script.

[Purpose]
 - Call API to query database
 - Parshing data and sort list, select information exact we need
 - Handle SSH session

[Function]
 - Query database with API and Make switch list with selected condition(Type, Region,...so on)
 - Gather current configuration and make a list
 - Deploy pre-configuration to target device via SSH session
 - Run command at target switch via SSH session

[Manual]
 - Query_DB.py              # Provide function for searching variable case depends on database
 - Check_config.py          # You can select function for variable case, then function call class for each vendor
     
        Find_Port_by_Description( [hostname], [vendor], [Target Circuit] )
            : Gather interface description for target circuit
        Find_Syslog_Config( [hostname], [vendor] )      
            : Gather syslog configuration
        Find_BGP_Group_Name_for_IX( [hostname], [vendor], [Target Port number] )
            : Gather BGP group name
        Find_BGP_DenyAll_Policy( [hostname], [vendor] )
            : Gather BGP policy(route-map) for stopping announcement
        *** Function will be update on next version
 - Run_Command.py           # Function handle SSH session and apply command
 
        Run_Command( [Hostname], [Vendor], [command], [ID], [Password])
            : Login device via SSH and execute command. Convert result to string and return result
        Apply_Config( [Hostname], [Vendor], [Config file location], [ID], [Password])
            : Read pre-configuration from local file(.txt). Login device via SSH and apply pre-configuration


[Requirement]
 - Python higher than 3.0
 - Netmiko library
 - Device login permission (TACACS+ account)


[Supported Vendor]
 - Juniper EX/QFX/MX series with JUNOS
 - Cisco Catalyst series with IOS
 - Cisco Nexus series with NXOS
 - Arista with EOS
 - Ubiquoss
 - Huawei
 - Foundry & Broucade
 - Dell
 - Ruijie
