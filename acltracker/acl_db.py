import mysql.connector
import logging
from acltracker.acl import *

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
			acl_dict = i.get_acl_dict()
			if acl_dict['fk_type'] != None and acl_dict['line'] != None and acl_dict['id'] != None:
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

#check list and split them into sets if they are new or not. Faster than stupid mysql queries and compare/update.
	def add_hcObj_ls(self, dev, name, new_hc_ls):
		ii_new = set(new_hc_ls)
		temp = self.get_hc_ls(dev,name)
		ii_add = list()
		ii_update = list()
		
		if temp:
			ii_db = set(temp)
			ii_add = ii_new - ii_db
			for hc in ii_add:
				hc_dict = hc.get_hc_dict()
				if hc_dict['fk_device'] and hc_dict['fk_acl_name']:
					self.__insert_hc__(hc_dict)
			self.connection.commit()
			
			ii_update = update_compare(ii_new,ii_db)
			if ii_update:
				for hc in ii_update:
					hc_dict = hc.get_hc_dict()
					if hc_dict['fk_device'] and hc_dict['fk_acl_name']:
						self.__update_hc__(hc_dict)
				self.connection.commit()
		else:
			for hc in ii_new:
				hc_dict = hc.get_hc_dict()
				if hc_dict['fk_device'] and hc_dict['fk_acl_name']:
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

	def update_hitcount_ls(self,hc_ls):
		return True

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

	def get_devices_weekscan(self):
		stmt = "SELECT * FROM `device` WHERE checked IS NULL or checked < now()- INTERVAL 7 DAY and fk_device_status = 1"
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

	def get_hc_ls(self, dev, name):
		stmt = ('SELECT * FROM hit_track WHERE fk_device = {0} and fk_acl_name = "{1}"'.format(int(dev),name))
		try:
			self.cursor.execute(stmt)
			hc = self.cursor.fetchall()
			hc_ls = list()
			for hit in hc:
				hc = (HitCount(dev = hit['fk_device'],name = hit['fk_acl_name'], dct_full = hit))
				hc_ls.append(hc)
			return hc_ls
		except mysql.connector.Error as err:
			logging.warning('There was an issue encountered: {}'.format(err))
			hc_ls = None
			return hc_ls

	#Fix - Once DB design settles down fix acl dict frame for full
	def get_acl_dct(self, full = False):
		if full:
			acl_dict = {'ACL': None,'line': None, 'Hits': None, 'Device': None, 'id': None, 'Type': None}
		else:
			acl_dict = {'ACL': None, 'Hits': None, 'Device': None, 'id': None, 'Type': None}


# Example update_acl(in in_acl varchar(400), in in_hash varchar(45), in in_hit int(4), in in_device int(2), in in_type varchar(45))
	def __insert_acl__(self, acl_dict):
		args = [acl_dict['acl'],acl_dict['line'],acl_dict['fk_device'], acl_dict['fk_type'], acl_dict['id']]
		result = self.cursor.callproc('add_record', args)
		return result

	def __insert_device__(self,ip):
		args = [ip]
		self.cursor.callproc('add_device', args)

	def __insert_acl_names__(self, acl_names):
		args = [acl_names['acl_name'],acl_names['iddevice']]
		self.cursor.callproc('add_acl_names',args)

	def __insert_hc__(self,hc):
		args = [hc['rule_uid'],hc['parent_uid'],hc['hit_count'],hc['last_hit_date'], hc['fk_device'], hc['fk_acl_name']]
		self.cursor.callproc('add_hit_count',args)
	
	def __update_hc__(self,hc):
		args = [hc['rule_uid'],hc['parent_uid'],hc['hit_count'],hc['last_hit_date'], hc['fk_device'], hc['fk_acl_name']]
		self.cursor.callproc('update_hit_count',args)

	def insert_rec(self, stmt, data):
		self.cursor.execute(stmt,data)
		return result 