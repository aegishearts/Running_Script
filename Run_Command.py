from netmiko import ConnectHandler, NetMikoAuthenticationException, NetMikoTimeoutException
import base64,requests,sys,re, time

### Ver1.0 ###

################################################################################
#USER = 'XXXXXXXXXXXXX' ### Operator KSS account
#PWENC = 'XXXXXXXXXXXX' ### base64 encode value with KSS password
#PW = base64.b64decode(PWENC).decode('ascii') ### decode value with encoded KSS password

Vendor_Code = {
        'cisco-nx':'cisco_nxos',
        'cisco':'cisco_ios',
        'ubiquoss':'cisco_ios',
        'huawei':'huawei',
        'juniper':'juniper_junos',
        'foundry':'brocade_netiron',
        'brocade_fabric':'brocade_fastiron',
        'dell':'dell_force10',
        'arista':'arista_eos',
        'ruijie':'cisco_ios',
}
################################################################################

def Run_Command(Hostname,VD,cmd,USER,PW):
	target = {
		'device_type': Vendor_Code[VD],
		'host': Hostname,
		'username': USER,
		'password': PW,
	}
	CNT = 0
	while True:
		if CNT == 2:
			print('Cannot make SSH session!! Need to check manually')
			RL = []
			return RL
		try:
	        	with ConnectHandler(**target) as net_connect:
        			if VD == 'cisco' or VD == 'ubiquoss':
                			output = net_connect.send_command_timing("term len 0")
        			elif VD == 'foundry':
                			output = net_connect.send_command_timing('skip-page-display')
        			elif VD == 'huawei':
                			output = net_connect.send_command_timing('screen-length 0 temporary')
        			output = net_connect.send_command_timing(cmd)
        			Result = output.splitlines()
				RL = []
				for i in Result:
					print(i)
					RL.append(str(i))      
  				return RL
		except (NetMikoAuthenticationException, NetMikoTimeoutException,):
			print('SSH Session is unstable!!! Try again after 3 seconds')
			time.sleep(3)
			CNT += 1
			continue

def Apply_Config(Hostname,VD,ConfigFile,USER,PW):
	target = {
        	'device_type': Vendor_Code[VD],
        	'host': Hostname,
	        'username': USER,
        	'password': PW,
   	}
	CNT = 0
	while True:
		if CNT == 2:
			print('Cannot make SSH session!! Need to check manually')
			return False
		elif VD == 'hitachi' or VD == 'Nortel':
			print('BCM Device!! Skip to configure this device')
			return False
		try:
	        	with ConnectHandler(**target) as net_connect:
				#### Huawei have issue. Need to troubleshoot
				print(ConfigFile)
        			output = net_connect.send_config_from_file(ConfigFile)
				print(output)
				if VD == 'juniper':
					net_connect.commit()
				elif VD == 'dell':
					net_connect.send_command_timing("end")
					net_connect.send_command_timing("wr me")
				elif VD == 'ubiquoss':
					net_connect.send_command_timing("wr me")
					net_connect.send_command_timing("y")
				else:
					net_connect.save_config()
				net_connect.disconnect()
				return True
		except (NetMikoAuthenticationException, NetMikoTimeoutException,):
			print('SSH Session is unstable!!! Try again after 3 seconds')
			time.sleep(3)
			CNT += 1
			continue
