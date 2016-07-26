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
		elif re.search('access-list', s_acl, re.I) and re.search('hitcnt=', s_acl, re.I) or re.search('fqdn',s_acl, re.I):
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
		acl_dict = {'fk_type': self.type,'line': self.line, 'id': self.id, 'Hits': self.hit_count, 'fk_device': self.device, 'acl': self.org_str}
		return acl_dict
	
	def __str__(self):
		return self.org_str


#Class based on cisco's brief access-list
#Example of DB return of HitCount Obj.
#{'rule_uid': '00146461', 'parent_uid': '419b789d', 'hit_count': '000002bf', 'last_hit_date': '5787f0a2', 'fk_hitcount_status': 1, 'fk_device':  2, 'fk_acl_name': 'acl_main'}
class HitCount:
	def __init__(self, dev = None, name = None, str_full = None, dct_full = None):
		if str_full: #Nate
			check = re.split(' ',str_full)
			for i in check:
				t = self.validate_hex(i)
				if not t:
					str_full = None
					break
			self.org_str = str_full
			self.acl_id = None
			self.acl_parent = None
			self.hit_count = None
			self.ls_hex_date = None
			self.lh_date = None
			self.last_update = None
			if self.parse_str(str_full):
				self.device = dev
				self.acl_name = name
			else:
				self.device = None
				self.acl_name = None
		elif dct_full != None:
			self.org_str = '%s %s %s %s' % (dct_full['rule_uid'],dct_full['parent_uid'],dct_full['hit_count'],dct_full['last_hit_date'])
			self.acl_id = self.validate_hex(dct_full['rule_uid'])
			self.acl_parent = self.validate_hex(dct_full['parent_uid'])
			self.hit_count = self.validate_hex(dct_full['hit_count'])
			self.ls_hex_date = self.validate_hex(dct_full['last_hit_date'])
			self.lh_date = self.shex_to_date(dct_full['last_hit_date'])
			self.device = dct_full['fk_device']
			self.acl_name = dct_full['fk_acl_name']
			self.last_update = dct_full['last_update']
		else:
			self.org_str = None
			self.acl_id = None
			self.acl_parent = None
			self.hit_count = None
			self.ls_hex_date = None


#Sets all based on string
	def parse_str(self,sHC):
		if sHC:
			ls_hex = re.split(' ',sHC)
			if len(ls_hex) == 4:
				self.acl_id = self.validate_hex(ls_hex[0])
				self.acl_parent = self.validate_hex(ls_hex[1])
				self.hit_count = self.validate_hex(ls_hex[2])
				self.ls_hex_date = self.validate_hex(ls_hex[3])
				self.lh_date = self.shex_to_date(ls_hex[3])
				return True
		else:
			return None
			
	def parse_dhitcount(self,dHC):
		if self.validate_hex(dct_full):
			self.acl_id = self.validate_hex(dct_full['acl_id'])
			self.acl_parent = self.validate_hex(dct_full['acl_parent'])
			self.hit_count = self.validate_hex(dct_full['hit_count'])
			self.ls_hex_date = self.validate_hex(dct_full['ls_hex_date'])
			self.lh_date = self.shex_to_date()

	def shex_to_date(self,h):
		t = datetime.datetime.fromtimestamp(self.shex_to_float(h))
		tt = t.strftime("%Y-%m-%d %H:%M:%S")
		return tt

	def shex_to_float(self,str):
		f = float(int(str,16))
		return f

	def validate_hex(self,str):
		if str != None:
			if re.match('^[A-F,a-f,0-9,X,x]{8}',str):
				return str
			else:
				return None

#hex string to Hex value
	def str_to_hex(self,str):
		h = hex(int(str,16))
		return h

	def get_hc_dict(self):
		d = {'rule_uid': self.acl_id, 'parent_uid': self.acl_parent,
			'hit_count':self.hit_count, 'last_hit_date':self.ls_hex_date,
			'fk_device': self.device, 'fk_acl_name': self.acl_name}
		return d

#OverRides
	def __str__(self):
		return self.org_str

	def __eq__(self,obj):
		if self.acl_id == obj.acl_id and self.device == obj.device and self.acl_name == obj.acl_name:
			return True
		else:
			return False

	def __hash__(self):
		return hash((self.acl_id,self.device,self.acl_name))

	def __hash_time__(self):
		return hash((self.acl_id,self.device,self.acl_name,self.ls_hex_date))



#*** acl methods on mass import ***
# loop through new HC objs and compared to old HC objs. If last hit changed update DB.
def update_compare(hc_new, hc_old):
	update = list()
	for hcn in hc_new:
		hash_id_new = hcn.__hash__()
		for hco in hc_old:
			hash_id_old = hco.__hash__()
			if hash_id_new == hash_id_old:
				if hcn.__hash_time__() != hco.__hash_time__():
					update.append(hcn)
				else:
					continue
			else:
				continue
	if len(update) > 0:
		return update
	else:
		return None

#Returns list of acls objects cleaned up
def parse_buffer_strs(buf_str):
	ls_strs = buf_str.split('\r\n')
	for i in range(0,len(ls_strs)):
		ls_strs[i] = ls_strs[i].strip()
	return ls_strs

#Returns a list of acl names on a device. Limit one device parse per call.
def parse_acl_names(ls_acl):
	ls_m = []
	ls_s = []
	for i in ls_acl:
		m = re.search('access-list ([A-Z,a-z,0-9,\-]+)', i)
		if m:
			ls_m.append(m.group(1))
	return ls_m

# Returns list of ACL objects (dict)
def imp_ls_acls(ls_acl, device_id):
	ls_acl_objs = list()
	for s_acl in ls_acl:
		a = ACL(s_acl, device_id)
		ls_acl_objs.append(a)
	return ls_acl_objs

#Returns list of HitCount (dict)
def imp_ls_hits_str(device,ls_hit,acl_name):
	ls_hit_objs = list()
	for s_hit in ls_hit:
		a = HitCount(dev = device, name = acl_name, str_full= s_hit)
		if a and a.acl_id:
			ls_hit_objs.append(a)
	return ls_hit_objs

def imp_ls_hits_db(device,db_hit,acl_name):
	ls_hit_objs = list()
	for db_hit in db_hit:
		a = HitCount(dev = device, name = acl_name, dct_full= db_hit)
		if a and a.acl_id:
			ls_hit_objs.append(a)
	return ls_hit_objs
