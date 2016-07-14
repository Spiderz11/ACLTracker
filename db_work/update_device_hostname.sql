DELIMITER $$

CREATE PROCEDURE `update_device_hostname` (in in_ip varchar(45), in in_hostname varchar(45))
BEGIN

	update device set host_name = in_hostname where ip = in_ip;

END$$

