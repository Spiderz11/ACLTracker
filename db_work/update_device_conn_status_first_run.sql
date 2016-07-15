CREATE PROCEDURE `update_device_conn_status_first_run` (in in_status int(1), in in_ip varchar(45), in in_id int(4))
BEGIN
	update device set fk_conn_status = in_status, checked = Current_Date where ip = in_ip and iddevice = in_id;
END