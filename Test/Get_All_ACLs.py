from acltracker import acl_db
from acltracker import device_session
from acltracker import acl
import datetime

import logging
import re
import time


#testing 
def inventory_devices():
	if test:
		device_list = [{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1},
			{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1}]
		for dev in device_list:
			get_inventory(dev)
	else:
		device_list = cursor.get_devices_weekscan()
		for dev in device_list:
			get_inventory(dev)


def inventory_device_hitcount():
	dev_acls = {'device': None,'ls_names': None}
	ls_full = list()
	if test:
		device_list = [{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1},
			{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1}]
		for dev in device_list:
			acl_name = cursor.get_acl_names(dev['iddevice'])
			get_hit_counters(dev,acl_name)
			
	else:
		device_list = cursor.get_good_devices()
		for dev in device_list:
			ls_full = cursor.get_acl_names(dev)
			get_hit_counters(dev, ls_full)

def get_inventory(dev):
	if dev['host_name'] == None:
		logging.info('Starting: ' + dev['ip'] + ' - Inventory All')
		logging.info(datetime.datetime.now())
	else:
		logging.info('Starting: ' + dev['host_name'] + ' - Inventory All')
		logging.info(datetime.datetime.now())
	session = device_session.Device_Session(dev,user,password)#Need to address from DB or input
	if session.connect_client():
		session.clear_buffer()
		if dev['host_name'] == None:
			dev['host_name'] = session.get_hostname()
			cursor.update_device_name(dev)
		session.send_command('\n')
		output = session.recv_small_buffer()
		if session.check_prompt(output) == False:
			if session.set_to_priv_access():
				#Paging goes back to the way it was once you disconnect
				if session.disable_paging():
					timeout,output = session.get_acls()
					#return is cleaned up list of acl strings
					acl_str = acl.parse_buffer_strs(output)
					acl_names = acl.parse_acl_names(acl_str)
					#return in list of ACL obj
					acl_obj = acl.imp_ls_acls(acl_str, dev['iddevice'])
					cursor.add_acl_name_ls(acl_names, dev['iddevice'])
					results = cursor.add_aclObj_ls(acl_obj)
					if timeout:
						dev['fk_conn_status'] = 2
					else:
						dev['fk_conn_status'] = 3
					cursor.update_device_conn_status(dev)
				else:
					results = False
		else:
			if session.disable_paging():
				timeout,output = session.get_acls()
				#return is cleaned up list of acl strings
				acl_str = acl.parse_buffer_strs(output)
				#return in list of ACL obj
				acl_obj = acl.imp_ls_acls(acl_str, dev['iddevice'])
				results = cursor.add_aclObj_ls(acl_obj)
				if timeout:
					dev['fk_conn_status'] = 2
				else:
					dev['fk_conn_status'] = 3
				cursor.update_device_conn_status(dev)
			else:
				results = False
			
		
		print(results)
	else:
		logging.warning('Connection could not be established. Task complete')
	logging.info(' Stopping: ' + dev['host_name'] + ' - Inventory All')
	logging.info(datetime.datetime.now())


def dev_connect(dev):
	session = device_session.Device_Session(dev,user,password)#Need to address from DB or input
	if session.connect_client():
		return session
	else: 
		return None
#Get all ACL brief. On ASA 'show access-list {acl_name} brief' show hex of all acls with > 0 hits.
def get_hit_counters(dev,ls_name): #Nate pickup from here.
	if dev['host_name'] == None:
		logging.info('Starting: ' + dev['ip'] + ' - Inventory All')
		logging.info(datetime.datetime.now())
	else:
		logging.info('Starting: ' + dev['host_name'] + ' - Inventory All')
		logging.info(datetime.datetime.now())
	session = device_session.Device_Session(dev,user,password)#Need to address from DB or input
	if session.connect_client():
		session.clear_buffer()
		session.send_command('\n')
		output = session.recv_small_buffer()
		if session.check_prompt(output) == False:
			if session.set_to_priv_access():
				#Paging goes back to the way it was once you disconnect
				if session.disable_paging():
					for name in ls_name:
						timeout,output = session.get_acl_brief(name['list_name'])
						#return is cleaned up list of hit strings
						ls_hit_str = acl.parse_buffer_strs(output)
						#return in list of HitCount obj
						hit_obj = acl.imp_ls_hits_str(dev['iddevice'],ls_hit_str,name['list_name'])
						results = cursor.add_hcObj_ls(dev['iddevice'],name['list_name'],hit_obj)
				else:
					results = False
		else:
			if session.disable_paging():
				for name in ls_name:
					output = session.get_acl_brief(name)
					#return is cleaned up list of hit strings
					ls_hit_str = acl.parse_buffer_strs(output)
					#return in list of HitCount obj
					hit_obj = acl.imp_ls_hits_str(dev['iddevice'],ls_hit_str,name)
					results = cursor.add_hcObj_ls(dev['iddevice'],name['list_name'], hit_obj)
			else:
				results = False
			
		
	print(results)
	if dev['host_name'] == None:
		logging.info('Stopping: ' + dev['ip'] + ' - Hit Counters')
		logging.info(datetime.datetime.now())
	else:
		logging.info('Stopping: ' + dev['host_name'] + ' - Hit Counters')
		logging.info(datetime.datetime.now())
	return False

'''
------ Script Space -----
'''
#fix a better u/p.
user = input("Please enter the user: ")
password = input("Please enter the password for %s: " % user)
print(datetime.datetime.now())
cursor = acl_db.ACL_DB()
output = ''
results = ''
test = False

#inventory_devices()
inventory_device_hitcount()
print(datetime.datetime.now())







