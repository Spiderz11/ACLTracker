CREATE PROCEDURE `add_record` (in in_acl varchar(400), in in_device int(2), in in_type int(1), in in_hash varchar(50))
BEGIN
call d_log((select concat('Checking Item: Statrting')));
if ((select count(*) from acl where hash_uid = in_hash) = 0)THEN
	begin
		call d_log((select concat('Item did Exist: Statrting')));
		insert into acl (acl, hash_uid, created, fk_device, fk_type) values (in_acl, in_hash, Current_Date, in_device, in_type);
	end;
end if;
END