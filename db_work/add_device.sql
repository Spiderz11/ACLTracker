CREATE PROCEDURE `add_device` (in in_ip varchar(45))
BEGIN
	if ((select count(*) from devices where ip = in_ip) = 0) then
		insert into device (ip) values (in_ip);
	end if;
END