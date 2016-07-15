from decimal import *
import logging
import paramiko
import re
import time

#Session is defined by the connection to the device. 
#Device dict example
# If blank in DB will be None type in dict.
#{'host_name': 'BIG-Site/admin', 'ip': '10.20.0.1', 'model': None, 'fk_conn_status': 1, 'iddevice': 121, 'checked': None, 'manufactor': None, 'fk_device_status': 1, 'fk_conn_type': 1}
class Device_Session:
	def __init__(self, d_device, username, password):
		self.ip_address = d_device['ip']
		self.password = password
		self.username = username
		self.hostname = d_device['host_name']
		self.client = None
		self.shell_client = None
		getcontext().prec = 2

	def get_name(self):
		if self.hostname == None:
			return self.ip_adress
		else:
			return self.hostname


	#True client connected. False client failed to connect.
	def connect_client(self):
		self.client = paramiko.SSHClient()
		self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		
		try:
			self.client.connect(self.ip_address, username= self.username, password= self.password, look_for_keys=False, allow_agent=False)
			self.shell_client = self.client.invoke_shell()
			print('Waiting 5 seconds for connection')
			time.sleep(5)
			return True
		except (paramiko.ssh_exception.AuthenticationException):
			logging.warning('connect_client: Password or username not valid on this Device')
			return False
		except (paramiko.ssh_exception.BadHostKeyException):
			logging.warning('Connect_client: Bad Host Key')
			return False
		except (paramiko.ssh_exception.SSHException):
			logging.warning('Connect_client: General exception Possible non-SSH')


	#Disconnects ssh client
	def disconnect_client(self):
		self.client.close()
		logging.info('Disconnected client')


	#clears out the buffer and dumps it. Use recv_buffer for collecting output
	def clear_buffer(self):
		while self.wait_buffer(Decimal(0.5)):
			output = self.shell_client.recv(10000)

	def check_command_error(self,output):
		if re.search('^ERROR:', output, re.MULTILINE):
			logging.warning('Error in command usage.')
			logging.warning(output)
			return True
		else:
			return False

	def recv_small_buffer(self):
		output = bytes
		out = ''
		while self.wait_buffer(Decimal(0.5)):
			output = self.shell_client.recv(10000)
			out = output.decode('utf-8')
		return out

	#Gets buffer until buffer has nothing left. Appends all to a string that is returned.
	#Return tuple of combined timeout true/false and full_buff collected  
	def recv_large_buffer(self,timeout):
		output = bytes()
		out = ''
		full_buff = ''
		prompt_found = 0
		timeout = Decimal(timeout)
		while self.wait_buffer(timeout):
			output = self.shell_client.recv(10000)
			out = output.decode('utf-8')
			if self.check_prompt(out):
				prompt_found = 1
				full_buff += out
				out = None
				return (True,full_buff)
			else:
				full_buff += out
				out = None
		
		if prompt_found == 0:
			return (False,full_buff)
		return True

	def get_hostname(self):
		output = ''
		out = ''
		if self.send_command('\n'):
			output = self.recv_small_buffer()
			output = output.strip()
			out = re.search('^[A-Z,a-z,0-9,\-,/]+', output, re.MULTILINE)
			return out.group(0)
		else:
			return None

	#Returns false if timer expires. Else returns true when recv_ready is True
	def wait_buffer(self,timeout):
		while self.shell_client.recv_ready() == False and timeout > Decimal(0.00):
			time.sleep(timeout)
			timeout -= Decimal(0.1)
		if timeout < Decimal(0.1):
			return False
		else:
			return True

	#Only moving from User EXEC to Privileged EXEC. Just enough to run ACL list.	
	def set_to_priv_access(self):
		self.clear_buffer()
		self.send_command('en\n')
		output = self.recv_small_buffer()
		match = re.search('Password: ', output, re.MULTILINE) #MULTILINE used because of blank line output
		if match:
			self.send_command(self.password + '\n')
			self.clear_buffer()
			self.send_command('\n')
			output = self.recv_small_buffer()
			if self.check_prompt(output):
				return True
			else:
				logging.warning('Did not get elevated permissions in Device')
				return False
		else:
			logging.warning('No password prompt found')
			return False

	# Prevents having to watch out for the More paging issue when collecting buffer.
	# This goes back to default once session ends
	def disable_paging(self):
		self.clear_buffer()
		command = 'terminal pager 0\n'
		self.send_command(command)
		output = self.recv_small_buffer()
		if self.check_command_error(output):
			logging.warning('Command used: ' + command)
			return False
		else:
			logging.info('Paging Disabled sucsessful')
			return True


	def get_acls(self):
		self.clear_buffer()
		command = 'show access-list\n'
		self.send_command(command)
		timeout,output = self.recv_large_buffer(Decimal(1.5))
		if self.check_command_error(output):
			logging.warning('Command used: ' + command)
			return False
		else:
			return (True,output)


	def get_acl_brief(self, acl_name):
		self.clear_buffer()
		command = 'show access-list ' + acl_name + ' brief\n'
		self.send_command(command)
		timeout,output = self.recv_large_buffer(Decimal(1.5)) #TBH - Need to add timeout to return to update device timeout.
		if self.check_command_error(output):
			logging.warning('Command used: ' + command)
			return False
		else:
			#Nate pick up from here.
			return (True,output)
		

		# Checking for the '#' symbol to indicate access level
	def check_prompt(self,output):
		if self.check_command_error(output):
			return False
		match = re.search('[#]', output, re.MULTILINE)
		if match:
			return True
		else:
			return False

	#If something sent the return will be True
	def send_command(self,command):
		bytes_sent = self.shell_client.send(command)
		if bytes_sent != 0:
			return True
		else:
			logging.warning('Not sure something sent')
			return False 