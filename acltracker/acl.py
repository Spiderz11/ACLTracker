import datetime
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
			self.line = None
			self.hit_count = None
			self.device = dev
			self.org_str = new_str
			self.parse_acl(new_str)
		elif isinstance(db_acl):
			self.type = db_acl['fk_type']
			self.id = db_acl['id']
			self.line = db_acl['line']
			self.hit_count = db_acl['Hits']
			if dev == None:
				self.device = db_acl['Device']
			else:
				self.device = dev
			self.org_str = db_acl['ACL']
		else:
			self.type = None
			self.id = None
			self.line = None
			self.hit_count = None
			self.org_str = None

	def parse_acl(self, s_acl):
		if re.search('^access-list', s_acl, re.I):
			self.set_type(s_acl)
			self.set_line(s_acl)
			self.set_id(s_acl)
			self.set_hit_count(s_acl)
			self.org_str = s_acl
		else:
			logging.info('Does not appear to be an ACL item: ' + s_acl)

	def set_line(self, s_acl):
		line_num = re.search('line ([0-9]+)', s_acl, re.I)
		if line_num != None:
			self.line = line_num.group(1)
		else:
			self.line = None

	def set_type(self, s_acl):
		if re.search('name hash:', s_acl, re.I):
			self.type = 1
		elif re.search('object-group', s_acl, re.I):
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
		acl_dict = {'Type': self.type,'line': self.line, 'id': self.id, 'Hits': self.hit_count, 'Device': self.device, 'ACL': self.org_str}
		return acl_dict
	
	def __str__(self):
		return self.org_str


#Class based on cisco's brief access-list
class HitCount:
	def __init__(self, str_full = None,dct_full = None):
		if str_full != None:
			self.org_str = str_full
			self.acl_id = None
			self.acl_parent = None
			self.hit_count = None
			self.ls_hex_date = None
			self.lh_date = None
			self.parse_shitcount(str_full)
		elif dct_full != None:
			self.org_str = '%s %s %s %s' % (dct_full['acl_id'],dct_full['acl_parent'],dct_full['hit_count'],dct_full['ls_hex_date'])
			self.acl_id = None
			self.acl_parent = None
			self.hit_count = None
			self.ls_hex_date = None
			self.lh_date = None
			self.parse_dhitcount(dct_full)


#Sets all based on string
	def parse_shitcount(sHC):
		ls_hex = re.split(' ',sHC)
		if validate_hex(ls_hex):
			self.acl_id = ls_hex[0]
			self.acl_parent = ls_hex[1]
			self.hit_count = str_to_hex(ls_hex[2])
			self.ls_hex_date = ls_hex[3]
			self.lh_date = shex_to_date(ls_hex[3])
			
			
	def parse_dhitcount(dHC):
		if validate_hex(dct_full):
			self.acl_id = dct_full['acl_id']
			self.acl_parent = dct_full['acl_parent']
			self.hit_count = str_to_hex(dct_full['hit_count'])
			self.ls_hex_date = dct_full['ls_hex_date']
			self.lh_date = shex_to_date()

	def shex_to_date(h):
		t = datetime.datetime.fromtimestamp(shex_to_float(h))
		tt = t.strftime("%Y-%m-%d %H:%M:%S")
		return tt

	def shex_to_float(str):
		f = float(int(str,16))
		return f

	def validate_hex(str = None, dct_full=None):
		if dct_full == None:
			if re.match('^[A-F,a-f,0-9,X,x]{8}',str):
				return True
			else:
				return False
		else:
			for i in dct_full:
				if not validate_hex(str = i):
					return False
			return True


#hex string to Hex value
	def str_to_hex(str):
		h = hex(int(str,16))
		return h

#*** acl methods on mass import ***
#Returns list of acls objects cleaned up
def parse_str_acls(buf_str):
	ls_acls = buf_str.split('\r\n')
	for i in range(0,len(ls_acls)):
		ls_acls[i] = ls_acls[i].strip()
	print(len(ls_acls))
	return ls_acls
	
#Returns a list of acl names on a device. Limit one device parse per call.
def parse_acl_names(ls_acl):
	ls_m = []
	ls_s = []
	for i in ls_acl:
		ls_m.append((re.search('access-list [A-Z,a-z,0-9,\-]+', i)))
	for i in ls_m:
		if i != None:
			temp = re.split(' ',i.group(0))
			if temp[1] not in ls_s:
				ls_s.append(temp[1])
	return ls_s

# Returns list of ACL objects (dict)
def imp_ls_acls(ls_acl, device_id):
	ls_acl_objs = list()
	for s_acl in ls_acl:
		a = ACL(s_acl, device_id)
		ls_acl_objs.append(a)
	return ls_acl_objs

#Returns list of HitCount (dict)
def imp_ls_hits(ls_hit):
	ls_hit_objs = list()
	for s_hit in ls_hit:
		a = HitCount(str_full= s_hit)
		ls_hit_objs.append(a)
	return ls_hit_objs
