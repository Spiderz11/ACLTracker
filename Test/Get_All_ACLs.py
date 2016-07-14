from acltracker import acl_db
from acltracker import device_session
from acltracker import acl
import datetime


import logging
import re
import time



'''
------ Script Space -----
'''
print(datetime.datetime.now())
cursor = acl_db.ACL_DB()
output = ''
device_list = cursor.get_good_devices()
results = ''
test = True

#testing 
if test:
	device_list = [{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1},
		{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1}]
	for dev in device_list:
		inventory_all(dev)
else:
	for dev in device_list:
		inventory_all(dev)


def inventory_all(dev):
	if dev['host_name'] == None:
		logging.info(datetime.datetime.now() + ' Starting: ' + dev['ip'] + ' - Inventory All')
	else:
		logging.info(datetime.datetime.now() + ' Starting: ' + dev['host_name'] + ' - Inventory All')

	session = device_session.Device_Session(dev[ip],'admin','admin')#Need to address from DB or input
	if session.connect_client():
		session.clear_buffer()
		session.send_command('\n')
		if dev['host_name'] == None:
			dev['host_name'] = session.get_hostname(dev)
		output = session.recv_small_buffer()
		if session.check_prompt(output) == False:
			if session.set_to_priv_access():
				#Paging goes back to the way it was once you disconnect
				if session.disable_paging():
					output = session.get_acls()
					#return is cleaned up list of acl strings
					acl_str = acl.parse_str_acls(output, dev['iddevice'])
					acl_names = acl.parse_acl_names(acl_str, dev['iddevice')
					#return in list of ACL obj
					acl_obj = acl.imp_ls_acls(acl_str, dev['iddevice'])
					results = cursor.add_aclObj_ls(acl_obj)
				else:
					results = False
		else:
			if session.disable_paging():
				output = session.get_acls()
				#return is cleaned up list of acl strings
				acl_str = acl.parse_str_acls(output, dev['iddevice'])
				#return in list of ACL obj
				acl_obj = acl.imp_ls_acls(acl_str, dev['iddevice'])
				results = cursor.add_aclObj_ls(acl_obj)
			else:
				results = False
			
		
		print(results)
	else:
		logging.warning('Connection could not be established. Task complete')
	logging.info(datetime.datetime.now() + ' Stopping: ' + dev['host_name'] + ' - Inventory All')

#Get all ACL brief. On ASA 'show access-list {acl_name} brief' show hex of all acls with > 0 hits.
def get_hit_counters(): #Nate pickup from here.
	return False









