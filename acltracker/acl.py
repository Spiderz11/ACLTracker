import re
import logging

#Takes a string and trys to determine if it is an ACE, ACL, or Not sure.
'''
When dealing with access lists there will be 3 types. ACL_Name, ACL, and ACE (access list entries).
ACL_Name: 		access-list TEST; 3 elements; name hash: 0xd37fdb2b
ACL       			access-list TEST line 1 extended permit ip object-group LAN any 0xeb9e6e99
			ACE:		access-list TEST line 1 extended permit ip 10.10.10.0 255.255.255.0 any (hitcnt=0) 0x365de33c
			ACE:		access-list TEST line 1 extended permit ip 10.10.20.0 255.255.255.0 any (hitcnt=0) 0xc98d1b29
			ACE:		access-list TEST line 1 extended permit ip 10.10.30.0 255.255.255.0 any (hitcnt=2342345222) 0x2a9982d3
Cisco HASH re match:
re.search(0x[0-9A-Fa-f]{8})

Hitcount re match:

'''
class ACL:
	log =  logging.getLogger('Mod_acl')
	fc = logging.FileHandler('acl.log')
	#Parsing should be incoming as a string. Any ACL from Database should come in form of dict.
	def __init__(self, new_str= None, dev= None, db_acl= None):
		if db_acl == None and new_str != None:
			self.type = None
			self.id = None
			self.hit_count = None
			self.device = dev
			self.org_str = new_str
			self.parse_acl(new_str)
		elif isinstance(db_acl, dict):
			self.type = db_acl['Type']
			self.id = db_acl['ID']
			self.hit_count = db_acl['Hits']
			if dev == None:
				self.device = db_acl['Device']
			else:
				self.device = dev
			self.org_str = db_acl['ACL']
		else:
			self.type = None
			self.id = None
			self.hit_count = None
			self.org_str = None

	def parse_acl(self, s_acl):
		if re.search('^access-list', s_acl, re.I):
			self.set_type(s_acl)
			self.set_id(s_acl)
			self.set_hit_count(s_acl)
			self.org_str = s_acl
		else:
			logging.info('Does not appear to be an ACL item: ' + s_acl)
			

	def set_type(self, s_acl):
		if re.search('name hash:', s_acl, re.I):
			self.type = 1
		elif re.search('object-group', s_acl, re.I) or re.search('host \d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', s_acl, re.I):
			self.type = 3
		elif re.search('access-list', s_acl, re.I) and re.search('hitcnt=', s_acl, re.I):
			self.type = 2
		else:
			self.type = None
			logging.info('Not Sure: ' + s_acl)

	def set_id(self, s_acl):
		result = re.search('0x[0-9A-Fa-f]{5,9}',s_acl)
		if result:
			self.id = result.group(0)
		else:
			logging.info('No hash in: ' + s_acl)


	def set_hit_count(self, s_acl):
		a_result = re.search('hitcnt=[0-9]{1,}', s_acl)
		if a_result:
			b_result = re.search('[0-9]{1,}', a_result.group(0))
			self.hit_count = int(b_result.group(0))
		else:
			if self.type == 3 or self.type == 1:
				return True
			else:
				logging.info('No hitcnt in: ' + s_acl)
	
	# access-list TEST line 1 extended permit ip 10.10.30.0 255.255.255.0 any (hitcnt=2342345222) 0x2a9982d3
	# acl_dict = {'Type': {1-3}, 'ID': '0x2a9982d3', 'Hits': int(2342345222), 'Device': 12 'ACL': 'access-list TEST line 1 extended permit ip 10.10.30.0 255.255.255.0 any (hitcnt=2342345222) 0x2a9982d3'}
	def get_acl_dict(self):
		acl_dict = {'Type': self.type, 'ID': self.id, 'Hits': self.hit_count, 'Device': self.device, 'ACL': self.org_str}
		return acl_dict
	
	def __str__(self):
		return self.org_str
		
#*** acl methods on mass import ***
#Returns list of acls objects cleaned up
def parse_str_acls(buf_str, device_id):
	ls_acls = buf_str.split('\r\n')
	for i in range(0,len(ls_acls)):
		ls_acls[i] = ls_acls[i].strip()
	print(len(ls_acls))
	return ls_acls
	
#Returns a list of acl names on a device. Limit one device parse per call.
def parse_acl_names(ls_acl, device_id):
	ls_m = []
	ls_s = []
	for i in ls_acl:
		ls_m.append((re.search('access-list [A-Z,a-z,0-9,\-]+', i)))
	for i in ls_m:
		if i != None:
			temp = re.split(' ',i.group(0))
			if temp[1] not in ls_s:
				ls_s.append(temp[1])
	
# Returns list of ACL objects (dict)
def imp_ls_acls(ls_acl, device_id):
	ls_acl_objs = list()
	for s_acl in ls_acl:
		a = ACL(s_acl, device_id)
		ls_acl_objs.append(a)
	return ls_acl_objs
	
	
	
	
	
