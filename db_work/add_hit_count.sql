CREATE PROCEDURE `add_hit_count` (in in_rule_uid varchar(45), in in_parent_uid varchar(45), in in_hit_count varchar(45), in in_last_hit_date varchar(45), in in_hit_status int, in in_dev int)
BEGIN
	if ((select count(*) from hit_track where rule_uid = in_rule_uid and parent_uid = in_parent_uid and fk_device = in_dev) = 0) then
		insert into hit_track (rule_uid, parent_uid, hit_count, last_hit_date, fk_hitcount_status, fk_device) values(in_rule_uid, in_parent_uid, in_hit_count, in_last_hit_date, in_hit_status, in_dev);
	end if;
END