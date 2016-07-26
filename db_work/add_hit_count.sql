CREATE PROCEDURE `add_hit_count` (in in_rule_uid varchar(45), in in_parent_uid varchar(45), in in_hit_count varchar(45), in in_last_hit_date varchar(45), in in_dev int, in in_acl_name varchar(45))
BEGIN
	insert into hit_track (rule_uid, parent_uid, hit_count, last_hit_date, fk_device, fk_acl_name) values(in_rule_uid, in_parent_uid, in_hit_count, in_last_hit_date, in_dev, in_acl_name);
END