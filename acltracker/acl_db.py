import mysql.connector
import logging
from acltracker.acl import ACL

class ACL_DB:
	def __init__(self):
		self.connection = None
		self.cursor = self.get_dict_connect()

	#Need error catching
	def get_dict_connect(self):
		try:
			self.connection = mysql.connector.connect(user= 'root', password= 'Atl@nt1c', database='acltrack')#Allow user credentials fix 
			#python does not turn on auto-commit by default. Huge pain in the ass troubleshooting that one.
			self.connection.autocommit = False
			self.cursor = self.connection.cursor(dictionary=True)
			return self.cursor
		except mysql.connector.Error as err:
			print("There was an issue encountered: {}".format(err))
			self.cursor = None
			return self.cursor

	#IN = ACL dictionary
	#acl_dict = {'Type': {1-3}, 'ID': '0x2a9982d3', 'Hits': int(2342345222), 'ACL': 'access-list TEST line 1 extended permit ip 10.10.30.0 255.255.255.0 any (hitcnt=2342345222) 0x2a9982d3'}
	def add_acl_dict(self, acl_dict):
		if acl_dict['Type'] != None:
			self.__insert_acl__(acl_dict)

	# The list is ACL objects.
	#Need to fix the counter so we get a better look into records inserted.
	def add_aclObj_ls(self, acl_obj_ls):
		ii_good = 0
		ii_bad = 0
		ii_unknown = 0
		for i in acl_obj_ls:
			#get dict from acl obj
			print(i)
			acl_dict = i.get_hc_dict()
			if acl_dict['Type'] != None and acl_dict['line'] != None and acl_dict['id'] != None:
				result = self.__insert_acl__(acl_dict)
				if result == 1:
					ii_good += 1
				elif result == 0:
					ii_bad += 1
				elif result != 0 and result != 1:
					ii_unknown += 1
			else: 
				ii_bad += 1
				logging.warning(i)
		self.connection.commit()
		count = {'Total':len(acl_obj_ls), 'Inserted': ii_good, 'Rejected': ii_bad, 'Unknown': ii_unknown}
		return count

	def add_hcObj_ls(self, hc_obj_ls):
		ii_all = len(hc_obj_ls)
		ii = 0
		for hc in hc_obj_ls:
			hc_dict = hc.get_hc_dict()
			if hc_dict['fk_device']:
				self.__insert_hc__(hc_dict)
		self.connection.commit()

	def add_acl_name_ls(self, acl_names_ls, dev_id):
		for n in acl_names_ls:
			self.__insert_acl_names__({'acl_name': n,'iddevice':dev_id})
		self.connection.commit()

	def add_device(self,ls_ip):
		for ip in ls_ip:
			self.__insert_device__(ip)
		self.connection.commit()
	
	def update_device_name(self,dev):
		if dev['host_name'] != None:
			args = [dev['ip'],dev['iddevice'],dev['host_name']]
			self.cursor.callproc('update_device_hostname',args)
			self.connection.commit()

	def update_device_conn_status(self,dev):
		args = [dev['fk_conn_status'], dev['ip'],dev['iddevice']]
		self.cursor.callproc('update_device_conn_status',args)
		self.connection.commit()

	#Fix - Work on views in mysql to handle device returns
	def get_good_devices(self):
		stmt = "SELECT * FROM device where fk_device_status = 1"
		try:
			self.cursor.execute(stmt)
			all_devices = self.cursor.fetchall()
			return all_devices
		except mysql.connector.Error as err:
			print("There was an issue encountered: {}".format(err))
			all_devices = None
			return all_devices

	def get_acl_names(self, device):
		stmt = "SELECT * FROM acl_names where fk_device = %d" % device['iddevice']
		try:
			self.cursor.execute(stmt)
			all_names = self.cursor.fetchall()
			return all_names
		except mysql.connector.Error as err:
			logging.warning('There was an issue encountered: {}'.format(err))
			all_names = None
			return all_names

	#Fix - Once DB design settles down fix acl dict frame for full
	def get_acl_dct(self, full = False):
		if full:
			acl_dict = {'ACL': None,'line': None, 'Hits': None, 'Device': None, 'id': None, 'Type': None}
		else:
			acl_dict = {'ACL': None, 'Hits': None, 'Device': None, 'id': None, 'Type': None}

# Example of raw acl: 
# {'ACL': 'access-list acl-inbound line 17 extended permit ip host 172.30.56.250 10.16.0.0 255.255.0.0 log informational interval 300 (hitcnt=0) 0xf44c609d', 'Hits': 0, 'Device': 1, 'ID': '0xf44c609d', 'Type': 'ACL_entry'}
# {'ACL': 'access-list acl-inbound line 17 extended permit ip host 172.30.56.250 10.16.0.0 255.254.0.0 log informational interval 300 (hitcnt=0) 0x6084ad72', 'Hits': 0, 'Device': 1, 'ID': '0x6084ad72', 'Type': 'ACL_entry'}

# Example update_acl(in in_acl varchar(400), in in_hash varchar(45), in in_hit int(4), in in_device int(2), in in_type varchar(45))
	def __insert_acl__(self, acl_dict):
		args = [acl_dict['ACL'],acl_dict['line'],acl_dict['Device'], acl_dict['Type'], acl_dict['id']]
		result = self.cursor.callproc('add_record', args)
		return result

	def __insert_device__(self,ip):
		args = [ip]
		self.cursor.callproc('add_device', args)

	def __insert_acl_names__(self, acl_names):
		args = [acl_names['acl_name'],acl_names['iddevice']]
		self.cursor.callproc('add_acl_names',args)
	
	#(in in_rule_uid varchar(45), in in_parent_uid varchar(45), in in_hit_count varchar(45), in in_last_hit_date varchar(45), in in_hit_status int, in in_dev int)
	# {'rule_uid': , 'parent_uid': , 'hit_count': ,'last_hit_date': , 'fk_hitcount_status': , 'fk_device': }
	def __insert_hc__(self,hc):
		args = [hc['rule_uid'],hc['parent_uid'],hc['hit_count'],hc['last_hit_date'],hc['fk_hitcount_status'], hc['fk_device']]
		self.cursor.callproc('add_hit_count',args)

	def insert_rec(self, stmt, data):
		self.cursor.execute(stmt,data)
		return result 