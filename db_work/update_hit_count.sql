CREATE PROCEDURE `update_hit_count` (in in_rule varchar(45),in in_parent varchar(45), in in_hc varchar(45), in in_hit_date varchar(45), in in_device int, in in_acl_name varchar(45))
BEGIN
	update hit_track set hit_count = in_hc, last_hit_date = in_hit_date, last_update = Current_Date where rule_uid = in_rule and parent_uid = in_parent and fk_device = in_device and fk_acl_name = in_acl_name;
END