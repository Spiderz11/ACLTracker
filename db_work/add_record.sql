CREATE PROCEDURE `add_record` (in in_acl varchar(400),in in_line int, in in_device int(2), in in_type int(1), in in_id varchar(50))
BEGIN
if ((select count(*) from acl where id = in_id and fk_device = in_device and line = in_line) = 0)THEN
	begin		
		insert into acl (acl, line, id, created, fk_device, fk_type) values (in_acl, in_line, in_id, Current_Date, in_device, in_type);
	end;
end if;
END