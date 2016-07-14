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
print('This test script goes out and connects to a device and pulls the ACL and puts it in the Database')
cursor = acl_db.ACL_DB()
output = ''
device_list = cursor.get_good_devices()
results = ''

session = device_session.Device_Session('192.168.191.4', 'admin', 'admin')
if session.connect_client():
	session.clear_buffer()
	session.send_command('\n')
	output = session.recv_small_buffer()
	if session.check_prompt(output) == False:
		if session.set_to_priv_access():
			#Paging goes back to the way it was once you disconnect
			if session.disable_paging():
				output = session.get_acls()
				#return is cleaned up list of acl strings
				acl_str = acl.parse_str_acls(output, 121)
				#return in list of ACL obj
				acl_obj = acl.imp_ls_acls(acl_str, 121)
				results = cursor.add_aclObj_ls(acl_obj)
			else:
				results = False
				
	else:
		if session.disable_paging():
			output = session.get_acls()
			#return is cleaned up list of acl strings
			acl_str = acl.parse_str_acls(output, 121)
			#return in list of ACL obj
			acl_obj = acl.imp_ls_acls(acl_str, 121)
			results = cursor.add_aclObj_ls(acl_obj)
		else:
			results = False
		
	
	print(results)
else:
	logging.warning('Connection could not be established. Task complete')
print(datetime.datetime.now())










