import requests, re

#### Ver1.0 ####

########################################################
requests.packages.urllib3.disable_warnings()

IHMS_SW_List_API = 'https://melon.cdnetworks.com/api/ihms/get_ihms_node.jsp'
NIDB_SW_List_API = 'https://melon.cdnetworks.com/network/nidb/api/get_nidb_switch_list.jsp'

ALL_Regex = re.compile(r'[bB][bB]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[aA][cC][cC]+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[aA][gG][gG]+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[rR][mM][cC]+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
BB1_Regex = re.compile(r'[bB][bB]+[0-1]*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
BB2_Regex = re.compile(r'[bB][bB]+[2]*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
BB3_Regex = re.compile(r'[bB][bB]+[3-9]*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ACC1_Regex = re.compile(r'[aA][cC][cC]+[0-1]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|ACC+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ACC2_Regex = re.compile(r'[aA][cC][cC]+[2]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|ACC+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ACC3_Regex = re.compile(r'[aA][cC][cC]+[3]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|ACC+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ACC4_Regex = re.compile(r'[aA][cC][cC]+[4]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|ACC+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ACC5_Regex = re.compile(r'[aA][cC][cC]+[5-9]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|ACC+\d+-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
AGG_Regex = re.compile(r'[aA][gG][gG]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
RMC1_Regex = re.compile(r'[rR][mM][cC]+[0-1]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
RMC2_Regex = re.compile(r'[rR][mM][cC]+[2]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
RMC3_Regex = re.compile(r'[rR][mM][cC]+[3-9]\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
ETC_Regex = re.compile(r'[sS][oO][dD]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[sS][sS][dD]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[sS][tT][kK]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*|[mM][nN][gG]+\d*-[a-zA-Z]+\d+-[a-zA-Z]+\d*')
### Exception = TEST/TUN/FW/BDR/OOB/AP/VPN/WLC

Regex = {
	'All':ALL_Regex,
	'BB1':BB1_Regex,
	'BB2':BB2_Regex,
	'BB3':BB3_Regex,
	'ACC1':ACC1_Regex,
	'ACC2':ACC2_Regex,
	'ACC3':ACC3_Regex,
	'ACC4':ACC4_Regex,
	'ACC5':ACC5_Regex,
	'AGG':AGG_Regex,
	'RMC1':RMC1_Regex,
	'RMC2':RMC2_Regex,
	'RMC3':RMC3_Regex,
	'ETC':ETC_Regex,
}

Office_POP_Code = ['10047','10048','10049','10437','10453','10454','10458']
Office_POP_List = ['kr1-sel','qkr-sel','uk2-lhr','crg3-sjc']
########################################################

def Search_Host_NIDB(Hostname):
	data = requests.get(NIDB_SW_List_API).text
	data_line = data.splitlines()
	for i in data_line:
		if Hostname in i:
			Vendor = i.split(':')[-1]
			POP_Code = i.split(':')[1]
			return str(Vendor),str(POP_Code)

def Search_POP_NIDB(Code):
	List = []
	data = requests.get(NIDB_SW_List_API).text
	data_line = data.splitlines()
	for i in data_line:
		if Code in i:
        	    	List.append(str(i.split(':')[0]))
	return List	

def Search_All_Device_by_POP(Code):
	Lower_Code = '|'+Code.lower()+'|'
	Upper_Code = '|'+Code.upper()+'|'
	data = requests.get(IHMS_SW_List_API).text
   	data_line = data.splitlines()
	for i in data_line:
		if Lower_Code in i or Upper_Code in i:
			NGPC = i.split('|')[1]
			Region = i.split('|')[6]
	SW_List = Search_POP_NIDB(NGPC)
	return SW_List

def Search_Device_by_Type(Type):
	List = []
	data = requests.get(NIDB_SW_List_API).text
   	data_line = data.splitlines()
	while '' in data_line:
		data_line.remove('')
	for i in data_line:
		Code = i.split(':')[1]
		POP = i.split(':')[2]
		if Code in Office_POP_Code:
                	print('Ignore Office/CNC/BCM network device')
		elif POP in Office_POP_List:
                	print('Ignore Office/CNC/BCM network device')
		elif 'rmc1-tat1-bom' in i:
			pass
            	else:
			host = Regex[Type]
		        if host.match(i):
			        List.append(str(host.findall(i)[0]))
	return List
