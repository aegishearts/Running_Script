import Run_Command as RUN
import Query_DB

import re

#### Ver1.0 ####

########################################################
CMD_Port_Description_Check = {
        'cisco-nx':'show interface description | include BDR | grep ',
        'cisco':'show interface description | include BDR ',
        'ubiquoss':'show interface description | include BDR ',
        'huawei':'display interface description | no-more | include BDR | include ',
        'juniper':'show interface description | no-more | match BDR | match ',
        'foundry':'show interface brief',
        'brocade_fabric':'show interface description | nomore | include BDR | include ',
        'dell':'show interface description | no-more | grep BDR | grep ',
        'arista':'show interface description | no-more | include BDR ',
}
CMD_Port_IP_Check = {
	'juniper':'show configuration interfaces ',
}
CMD_BGP_Group_Check = {
        'juniper':'show configuration protocols bgp | display set | match ',
}
CMD_BGP_DenyAll_Policy = {
        'juniper':'show configuration policy-options | display set | match DENY-ANY',
}
CMD_Syslog_Config = {
	'juniper':'show configuration system syslog | display set | no-more',
	'foundry':'show run | include logging',
	'cisco':'show run | include logging',
	'cisco-nx':'show run | include logging | no-more',
	'ubiquoss':'show run | include logging',
	'dell':'show run | grep logging',
	'arista':'show run | include logging',
	'brocade_fabric':'show run | include logging',
	'huawei':'display current-configuration | include info-center',
}
Regex_IPv4_Host = re.compile(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$")
Regex_IPv6_Host = re.compile(r'^\d{1,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}\d{0,4}:{0,2}')
Regex_Syslog_level = re.compile(r'local[0-7]')
########################################################

class JUNOS():
	def Interface_LocalIP_check(self,Host, Vendor, Port):
		CMD = CMD_Port_IP_Check[Vendor]+Port+' | display set'
    		RL = RUN.Run_Command(Host, Vendor, CMD)
    		for i in RL:
	    		if ' family inet address ' in i:
		    		LocalIP_Mask = i.split()[-1]
				LocalIP = Regex_IPv4_Host.findall(LocalIP_Mask)
    		return LocalIP[0]
	def BGP_Group_check_for_IX(self,Host, Vendor,Port_Info):
		BGP_Group_List = []
	    	BGP_Group_DIC = {}
		for i in Port_Info.keys():
			LocalIP = Port_Info[i][0]
        	    	CMD = CMD_BGP_Group_Check[Vendor]+'\"local-address '+LocalIP+'\"'
    			RL = RUN.Run_Command(Host, Vendor, CMD)
	    		for j in RL:
		    		if 'set protocols bgp group ' in j and LocalIP in j:
			    		BGP_Name = j.split()[4]
				    	if not BGP_Name in BGP_Group_List:
						BGP_Group_List.append(BGP_Name)
    		for i in BGP_Group_List:
	    		IMP_List = []
		    	EXP_List = []
                    	CMD = CMD_BGP_Group_Check[Vendor]+'\" '+i+' import\"'
    			RL = RUN.Run_Command(Host, Vendor, CMD)
	    		for j in RL:
		    		if 'set protocols bgp group ' in j and ' import ' in j:
			    		IMP_Name = j.split()[-1]
				    	IMP_List.append(IMP_Name)
                    	CMD = CMD_BGP_Group_Check[Vendor]+'\" '+i+' export\"'
	    		RL = RUN.Run_Command(Host, Vendor, CMD)
		    	for j in RL:
				if 'set protocols bgp group ' in j and ' export ' in j:
					EXP_Name = j.split()[-1]
    					EXP_List.append(EXP_Name)
	    		BGP_Group_DIC[i] = [IMP_List,EXP_List]	
    		return BGP_Group_DIC
    	def Description_check(self,Host, Vendor,CID_List):
		PT_DIC = {}
    		for i in CID_List:
	    		CMD = CMD_Port_Description_Check[Vendor]+i
		    	RL = RUN.Run_Command(Host, Vendor, CMD)
    			for j in RL:
	    			if i in j and 'IX' in j:
		    			LocalIP = j.split()[-1].split(':')[5]
			    		Port = j.split()[0]
				    	PT_DIC[Port] = [LocalIP,'']
    				elif i in j:
	    				PeerIP = j.split()[-1].split(':')[5]
		    			Port = j.split()[0]
			    		LocalIP = JUNOS_Interface_LocalIP_check(Host, Vendor, Port)
				PT_DIC[Port] = [LocalIP, PeerIP]
    		if not PT_DIC == {}:
	    		return PT_DIC
	def BGP_DenyAll_Policy(self,Host, Vendor):
    		CMD = CMD_BGP_DenyAll_Policy[Vendor]
	    	RL = RUN.Run_Command(Host, Vendor, CMD)
    		PL_Name = ''
	    	for i in RL:
			if 'set policy-options policy-statement ' in i and 'DENY-ANY' in i:
				Name = i.split()[3]
    				if PL_Name == '':
	    				PL_Name = Name
    		return PL_Name
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
        	Server_DIC = {}
        	SRC = ''
        	for i in RL:
            		if 'source-address ' in i:
                		SRC = i.split()[-1]
            		elif 'facility-override ' in i:
                		IP = i.split()[-3]
                		Level = i.split()[-1]
                		Server_DIC[IP] = Level
		return Server_DIC, SRC

class Foundry():
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
        	Server_List = []
		Server_DIC = {}
        	SRC = ''
		Level = ''
        	for i in RL:
            		if 'logging host ' in i:
                		IP = i.split()[-1]
				Server_List.append(IP)
            		elif 'logging facility ' in i:
                		Level = i.split()[-1]
		for i in Server_List:
			Server_DIC[i] = Level
		return Server_DIC, SRC

class Brocade():
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
        	Server_List = []
		Server_DIC = {}
        	SRC = ''
		Level = ''
        	for i in RL:
            		if 'logging syslog-server ' in i:
                		IP = i.split()[-1]
				Server_List.append(IP)
            		elif 'logging syslog-facility ' in i:
                		Level = i.split()[-1]
		for i in Server_List:
			Server_DIC[i] = Level
		return Server_DIC, SRC

class Huawei():
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
        	Server_List = []
		Server_DIC = {}
        	SRC = ''
		Level = ''
        	for i in RL:
            		if 'info-center loghost ' in i and 'facility local' in i:
                		IP = i.split()[2]
                		Level = i.split()[-1]
				Server_DIC[IP] = Level
            		elif 'info-center loghost ' in i and 'source ' in i:
				SRC = i.split()[-1]
            		elif 'info-center loghost ' in i and 'source-ip' in i:
                		SRC = i.split()[4]
		return Server_DIC, SRC

class IOS():
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
        	Server_List = []
		Server_DIC = {}
        	SRC = ''
		Level = ''
        	for i in RL:
            		if 'logging ' in i and Regex_IPv4_Host.match(i.split()[-1]):
                		IP = Regex_IPv4_Host.findall(i.split()[-1])
				Server_List.append(IP[0])
            		elif 'logging facility ' in i:
                		Level = i.split()[-1]
			elif 'logging source-interface' in i:
				if Vendor == 'dell':
					SRC = i.split()[-2]+i.split()[-1]
				else:
					SRC = i.split()[-1]
		for i in Server_List:
			Server_DIC[i] = Level
		return Server_DIC, SRC

class NXOS():
    	def Syslog_Config(self,Host, Vendor):
        	CMD = CMD_Syslog_Config[Vendor]
        	RL = RUN.Run_Command(Host, Vendor, CMD)
		Server_DIC = {}
        	SRC = ''
        	for i in RL:
            		if 'logging server ' in i:
                		IP = i.split()[2]
                		Level = i.split()[-1]
				Server_DIC[IP] = Level
			elif 'logging source-interface' in i:
				SRC = i.split()[-1]
			else:
				Level = ''
		return Server_DIC, SRC

def Find_Port_by_Description(Host, Vendor, CID_List):
	if Vendor == 'juniper':
		DIC = JUNOS.Description_check(Host, Vendor,CID_List)
	return DIC

def Find_BGP_Group_Name_for_IX(Host, Vendor, Port_Info):
	if Vendor == 'juniper':
		DIC = JUNOS.BGP_Group_check_for_IX(Host, Vendor,Port_Info)
	return DIC

def Find_BGP_DenyAll_Policy(Host, Vendor):
	if Vendor == 'juniper':
		Name = JUNOS.BGP_DenyAll_Policy(Host, Vendor)
	return Name

def Find_Syslog_Config(Host, Vendor):
	if Vendor == 'juniper':
        	IPs,SRC = JUNOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'foundry':
        	IPs,SRC = Foundry().Syslog_Config(Host, Vendor)
	elif Vendor == 'cisco':
        	IPs,SRC = IOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'cisco-nx':
        	IPs,SRC = NXOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'ubiquoss':
        	IPs,SRC = IOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'dell':
        	IPs,SRC = IOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'arista':
        	IPs,SRC = IOS().Syslog_Config(Host, Vendor)
	elif Vendor == 'brocade_fabric':
        	IPs,SRC = Brocade().Syslog_Config(Host, Vendor)
	elif Vendor == 'huawei':
        	IPs,SRC = Huawei().Syslog_Config(Host, Vendor)
	elif Vendor == 'ruijie':
        	IPs,SRC = IOS().Syslog_Config(Host, 'cisco')
	print(Host)
	print(IPs)
	return IPs,SRC
