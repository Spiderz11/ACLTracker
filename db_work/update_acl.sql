create procedure update_acl(in in_acl varchar(400), in in_hash varchar(45), in in_hit int(4), in in_device int(2), in in_type int(1), out out_row_affected varchar(45))
begin

declare old_hit int(4);
declare checkd datetime;
declare lastd datetime;
declare hit_status varchar(45);

call d_log((select concat('in_acl = ',in_acl,' in_hash = ', in_hash, ' in_hit = ', in_hit, ' in_device = ', in_device, ' in_type = ', in_type)));

	if ((select count(*) from acl where acl.hash_uid = in_hash and fk_device = in_device)> 0) then
		begin
			call d_log((select concat('Item did Exist: Statrting')));
			select hitcount, checked, lasthit, fk_hitcount_status
			into old_hit, checkd, lastd, hit_status
			from acl
			where acl.hash_uid = in_hash and fk_device = in_device;    
			-- check and update acl hitcount, fk_hitcount_status, checked, and lasthit --
			-- fk_hitcount_status: 1 = 'No Change', 2 = 'Changed', 3 = 'Reset'        --
			case in_hit
				when in_hit = old_hit && in_hit != 0 then
					begin
						update acl set checked = Current_Date, fk_hitcount_status = 1 where acl.hash_uid = in_hash and fk_device = in_device;
						set out_row_affected = row_count();
					end;
				when in_hit < old_hit && in_hit > 0 then 
					begin
						update acl set checked = Current_Date, hitcount = in_hit, lasthit = Current_Date, fk_hitcount_status = 2 where acl.hash_uid = in_hash and fk_device = in_device;
						set out_row_affected = row_count();
					end;
				when in_hit = 0 && in_hit < old_hit then 
					begin
						update acl set checked = Current_Date, hitcount = in_hit, fk_hitcount_status = 3 where acl.hash_uid = in_hash and fk_device = in_device;
						set out_row_affected = row_count();
					end;
				when in_hit = 0 && in_hit = old_hit then # checking if both in_hit and old_hit are 0
					begin
						if (hit_status = 3 && timestampdiff(day,old_hit,Current_Date)>6) then
							update acl set checked = Current_Date, fk_hitcount_status = 1 where acl.hash_uid = in_hash and fk_device = in_device;
							set out_row_affected = row_count();
						elseif (hit_status = 3 && timestampdiff(day,old_hit,Current_Date)<=6) then
							update acl set checked = Current_Date where acl.hash_uid = in_hash and fk_device = in_device;
							set out_row_affected = row_count();
						end if;
					end;
				when in_hit > old_hit then 
					begin
						update acl set checked = Current_Date, hitcount = in_hit, lasthit = Current_Date, fk_hitcount_status = 2 where acl.hash_uid = in_hash and fk_device = in_device;
						set out_row_affected = row_count();
					end;
				else 
					begin
						call d_log((select concat('End of case no match found')));
					end;
			end case;
		end;
	else
		begin
			call d_log((select concat('Item did not Exist. Trying to insert.')));
			if (in_type = 2) then
				begin
					call d_log((select concat('Item being inserted is ACE')));
                    call d_log((select concat('insert into acl (acl, hash_uid, hitcount, checked, lasthit, fk_device, fk_type, fk_hitcount_status) values (',in_acl,',',in_hash,',',in_hit,',',Current_Date,',',Current_Date,',',in_device,',',in_type,',',3)));
					insert into acl (acl, hash_uid, hitcount, created, checked, lasthit, fk_device, fk_type, fk_hitcount_status) values (in_acl, in_hash, in_hit,Current_Date, Current_Date, Current_Date, in_device, in_type, 3);					
                    set out_row_affected = row_count();
				end;
			else
				begin
					call d_log((select concat('Item being inserted is Not ACE')));
					insert into acl (acl, hash_uid, hitcount, created, checked, lasthit, fk_device, fk_type, fk_hitcount_status) values (in_acl, in_hash, 0,Current_Date, Current_Date, Current_Date, in_device, in_type, 3);
                    set out_row_affected = row_count();
				end;
			end if;
		end;
	end if;
end;