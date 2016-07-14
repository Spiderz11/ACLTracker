CREATE PROCEDURE `add_acl_names` (in in_name varchar(45), in in_device_id int(2))
BEGIN
if ((select count(*) from acl_names where acl_names.list_name = in_name and acl_names.fk_device = in_device_id) = 0) then
	begin
		insert into acl_names (list_name, fk_device) values (in_name, in_device_id);
    end;
end if;
END;