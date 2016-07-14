-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema ACLTrack
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema ACLTrack
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `ACLTrack` DEFAULT CHARACTER SET utf8 ;
USE `ACLTrack` ;

-- -----------------------------------------------------
-- Table `ACLTrack`.`conn_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`conn_status` (
  `idconn_Status` INT NOT NULL AUTO_INCREMENT,
  `status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idconn_Status`),
  UNIQUE INDEX `idconn_Status_UNIQUE` (`idconn_Status` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`device_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`device_status` (
  `iddevice_status` INT NOT NULL AUTO_INCREMENT,
  `status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`iddevice_status`),
  UNIQUE INDEX `iddevice_status_UNIQUE` (`iddevice_status` ASC),
  UNIQUE INDEX `status_UNIQUE` (`status` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`device`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`device` (
  `iddevice` INT NOT NULL AUTO_INCREMENT,
  `host_name` VARCHAR(45) NULL,
  `ip` VARCHAR(45) NOT NULL,
  `manufactor` VARCHAR(45) NULL,
  `model` VARCHAR(45) NULL,
  `connection` VARCHAR(45) NULL,
  `fk_conn_status` INT NOT NULL DEFAULT 1,
  `fk_device_status` INT NOT NULL DEFAULT 1,
  UNIQUE INDEX `idDevice_UNIQUE` (`iddevice` ASC),
  INDEX `fk_Device_conn_Status1_idx` (`fk_conn_status` ASC),
  INDEX `fk_Device_device_status1_idx` (`fk_device_status` ASC),
  PRIMARY KEY (`iddevice`, `ip`),
  CONSTRAINT `fk_Device_conn_Status1`
    FOREIGN KEY (`fk_conn_status`)
    REFERENCES `ACLTrack`.`conn_status` (`idconn_Status`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Device_device_status1`
    FOREIGN KEY (`fk_device_status`)
    REFERENCES `ACLTrack`.`device_status` (`iddevice_status`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`acl_type`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`acl_type` (
  `idacl_type` INT NOT NULL AUTO_INCREMENT,
  `cat` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idacl_type`),
  UNIQUE INDEX `idacl_type_UNIQUE` (`idacl_type` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`hitcount_status`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`hitcount_status` (
  `idhitcount_status` INT NOT NULL AUTO_INCREMENT,
  `status` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idhitcount_status`),
  UNIQUE INDEX `idhitcount_status_UNIQUE` (`idhitcount_status` ASC),
  UNIQUE INDEX `status_UNIQUE` (`status` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`acl_error`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`acl_error` (
  `idacl_error` INT NOT NULL AUTO_INCREMENT,
  `error` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`idacl_error`),
  UNIQUE INDEX `idacl_error_UNIQUE` (`idacl_error` ASC),
  UNIQUE INDEX `error_UNIQUE` (`error` ASC))
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`acl`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`acl` (
  `idacl` INT NOT NULL AUTO_INCREMENT,
  `acl` VARCHAR(400) NOT NULL,
  `hash_uid` VARCHAR(45) NOT NULL,
  `hitcount` INT NULL,
  `checked` DATE NOT NULL,
  `lasthit` DATE NULL,
  `fk_device` INT NOT NULL,
  `fk_type` INT NOT NULL,
  `fk_hitcount_status` INT NOT NULL DEFAULT 3,
  `fk_acl_error` INT NOT NULL DEFAULT 1,
  PRIMARY KEY (`fk_device`, `hash_uid`),
  UNIQUE INDEX `idacl_UNIQUE` (`idacl` ASC),
  INDEX `fk_acl_Device_idx` (`fk_device` ASC),
  INDEX `fk_acl_acl_type1_idx` (`fk_type` ASC),
  INDEX `fk_acl_hitcount_status1_idx` (`fk_hitcount_status` ASC),
  INDEX `fk_acl_acl_error1_idx` (`fk_acl_error` ASC),
  CONSTRAINT `fk_acl_Device`
    FOREIGN KEY (`fk_device`)
    REFERENCES `ACLTrack`.`device` (`iddevice`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_acl_acl_type1`
    FOREIGN KEY (`fk_type`)
    REFERENCES `ACLTrack`.`acl_type` (`idacl_type`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_acl_hitcount_status1`
    FOREIGN KEY (`fk_hitcount_status`)
    REFERENCES `ACLTrack`.`hitcount_status` (`idhitcount_status`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_acl_acl_error1`
    FOREIGN KEY (`fk_acl_error`)
    REFERENCES `ACLTrack`.`acl_error` (`idacl_error`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`acl_removed_bak`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`acl_removed_bak` (
  `idacl` INT NOT NULL AUTO_INCREMENT,
  `acl` VARCHAR(400) NOT NULL,
  `hash_uid` VARCHAR(45) NOT NULL,
  `hitcount` INT ZEROFILL NOT NULL,
  `checked` DATETIME NOT NULL,
  `lasthit` DATETIME NULL,
  `fk_device` INT NOT NULL,
  `fk_type` INT NOT NULL,
  `fk_hitcount_status` INT NOT NULL,
  `removed` DATETIME NOT NULL,
  PRIMARY KEY (`idacl`),
  UNIQUE INDEX `idacl_UNIQUE` (`idacl` ASC),
  INDEX `fk_acl_Device_idx` (`fk_device` ASC),
  INDEX `fk_acl_acl_type1_idx` (`fk_type` ASC),
  INDEX `fk_acl_hitcount_status1_idx` (`fk_hitcount_status` ASC),
  CONSTRAINT `fk_acl_Device0`
    FOREIGN KEY (`fk_device`)
    REFERENCES `ACLTrack`.`device` (`iddevice`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_acl_acl_type10`
    FOREIGN KEY (`fk_type`)
    REFERENCES `ACLTrack`.`acl_type` (`idacl_type`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_acl_hitcount_status10`
    FOREIGN KEY (`fk_hitcount_status`)
    REFERENCES `ACLTrack`.`hitcount_status` (`idhitcount_status`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `ACLTrack`.`dbug_log`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`dbug_log` (
  `iddbug_log` INT NOT NULL AUTO_INCREMENT,
  `entry` VARCHAR(2000) NULL,
  PRIMARY KEY (`iddbug_log`))
ENGINE = InnoDB;

USE `ACLTrack` ;

-- -----------------------------------------------------
-- Placeholder table for view `ACLTrack`.`over30`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`over30` (`Device_Name` INT, `Ip_Address` INT, `Category` INT, `Hitcount` INT, `Last_Date_Checked` INT, `Last_Hit_Date` INT, `ACL` INT);

-- -----------------------------------------------------
-- Placeholder table for view `ACLTrack`.`over60`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`over60` (`Device_Name` INT, `Ip_Address` INT, `Category` INT, `Hitcount` INT, `Last_Date_Checked` INT, `Last_Hit_Date` INT, `ACL` INT);

-- -----------------------------------------------------
-- Placeholder table for view `ACLTrack`.`over90`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`over90` (`Device_Name` INT, `Ip_Address` INT, `Category` INT, `Hitcount` INT, `Last_Date_Checked` INT, `Last_Hit_Date` INT, `ACL` INT);

-- -----------------------------------------------------
-- Placeholder table for view `ACLTrack`.`get_all_good_devices`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `ACLTrack`.`get_all_good_devices` (`ID` INT, `IP` INT);

-- -----------------------------------------------------
-- procedure update_acl
-- -----------------------------------------------------

DELIMITER $$
USE `ACLTrack`$$
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
					insert into acl (acl, hash_uid, hitcount, checked, lasthit, fk_device, fk_type, fk_hitcount_status) values (in_acl, in_hash, in_hit, Current_Date, Current_Date, in_device, in_type, 3);					
                    set out_row_affected = row_count();
				end;
			else
				begin
					call d_log((select concat('Item being inserted is Not ACE')));
					insert into acl (acl, hash_uid, hitcount, checked, lasthit, fk_device, fk_type, fk_hitcount_status) values (in_acl, in_hash, 0, Current_Date, Current_Date, in_device, in_type, 3);
                    set out_row_affected = row_count();
				end;
			end if;
		end;
	end if;
end;$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure duplicate_check
-- -----------------------------------------------------

DELIMITER $$
USE `ACLTrack`$$
# slfksl 
CREATE PROCEDURE `duplicate_check` (in in_hash varchar(45), in in_device int(2))
BEGIN
if ((select count(*) from acl where acl.hash_uid = in_hash and acl.fk_device = in_device)>1) then
	begin
		update acl set fk_acl_error = 1 where acl.hash_uid = in_hash and acl.fk_device = in_device; 
    end;
end if;
END;$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure remove_duplicate
-- -----------------------------------------------------

DELIMITER $$
USE `ACLTrack`$$
CREATE PROCEDURE `remove_duplicate` ()
BEGIN
	
END$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure d_log
-- -----------------------------------------------------

DELIMITER $$
USE `ACLTrack`$$
create procedure d_log(in in_acl varchar(2000))
begin
	insert into dbug_log (entry) values (in_acl);
end;$$

DELIMITER ;

-- -----------------------------------------------------
-- procedure add_record
-- -----------------------------------------------------

DELIMITER $$
USE `ACLTrack`$$
CREATE PROCEDURE `add_record` (in in_acl varchar(400), in in_hash varchar(45), in in_hit int(4), in in_device int(2), in in_type int(1))
BEGIN
insert into acl (acl, hash_uid, hitcount, checked, lasthit, fk_device, fk_type) values (in_acl, in_hash, in_hit, Current_Date, Current_Date, in_device, in_type);
END$$

DELIMITER ;

-- -----------------------------------------------------
-- View `ACLTrack`.`over30`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ACLTrack`.`over30`;
USE `ACLTrack`;
CREATE  OR REPLACE VIEW `over30` AS SELECT 
device.host_name as Device_Name,
device.ip as Ip_Address,
acl_type.cat as Category,
acl.hitcount as Hitcount,
acl.checked as Last_Date_Checked,
acl.lasthit as Last_Hit_Date,
acl.acl as ACL
FROM device, acl, acl_type
WHERE
device.iddevice = acl.fk_device
AND acl.fk_type = acl_type.idacl_type
AND timestampdiff(day,acl.lasthit,now())>=30
AND timestampdiff(day, acl.lasthit, now()) < 60;

-- -----------------------------------------------------
-- View `ACLTrack`.`over60`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ACLTrack`.`over60`;
USE `ACLTrack`;
CREATE  OR REPLACE VIEW `over60` AS SELECT 
device.host_name as Device_Name,
device.ip as Ip_Address,
acl_type.cat as Category,
acl.hitcount as Hitcount,
acl.checked as Last_Date_Checked,
acl.lasthit as Last_Hit_Date,
acl.acl as ACL
FROM device, acl, acl_type
WHERE
device.iddevice = acl.fk_device
AND acl.fk_type = acl_type.idacl_type
AND timestampdiff(day,acl.lasthit,now())>=60
AND timestampdiff(day, acl.lasthit, now()) < 90;

-- -----------------------------------------------------
-- View `ACLTrack`.`over90`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ACLTrack`.`over90`;
USE `ACLTrack`;
CREATE  OR REPLACE VIEW `over90` AS SELECT 
device.host_name as Device_Name,
device.ip as Ip_Address,
acl_type.cat as Category,
acl.hitcount as Hitcount,
acl.checked as Last_Date_Checked,
acl.lasthit as Last_Hit_Date,
acl.acl as ACL
FROM device, acl, acl_type
WHERE
device.iddevice = acl.fk_device
AND acl.fk_type = acl_type.idacl_type
AND timestampdiff(day,acl.lasthit,now())>=90;

-- -----------------------------------------------------
-- View `ACLTrack`.`get_all_good_devices`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `ACLTrack`.`get_all_good_devices`;
USE `ACLTrack`;
-- 1 = Unknown, 2 = Good , 3 = Time out, 4 = Bad login, 5 = Prompt error
CREATE  OR REPLACE VIEW `get_all_good_devices` AS SELECT
device.iddevice as ID,
device.ip as IP
from Device
where fk_device_status = 2;

SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;

-- -----------------------------------------------------
-- Data for table `ACLTrack`.`conn_status`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`conn_status` (`idconn_Status`, `status`) VALUES (1, 'Unknown');
INSERT INTO `ACLTrack`.`conn_status` (`idconn_Status`, `status`) VALUES (2, 'Good');
INSERT INTO `ACLTrack`.`conn_status` (`idconn_Status`, `status`) VALUES (3, 'Time out');
INSERT INTO `ACLTrack`.`conn_status` (`idconn_Status`, `status`) VALUES (4, 'Bad login');
INSERT INTO `ACLTrack`.`conn_status` (`idconn_Status`, `status`) VALUES (5, 'Prompt error');

COMMIT;


-- -----------------------------------------------------
-- Data for table `ACLTrack`.`device_status`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`device_status` (`iddevice_status`, `status`) VALUES (1, 'Enabled');
INSERT INTO `ACLTrack`.`device_status` (`iddevice_status`, `status`) VALUES (2, 'Disabled');

COMMIT;


-- -----------------------------------------------------
-- Data for table `ACLTrack`.`device`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`device` (`iddevice`, `host_name`, `ip`, `manufactor`, `model`, `connection`, `fk_conn_status`, `fk_device_status`) VALUES (1, NULL, 'unknown', 'unknown', 'unknown', 'ssh', 1, 1);
INSERT INTO `ACLTrack`.`device` (`iddevice`, `host_name`, `ip`, `manufactor`, `model`, `connection`, `fk_conn_status`, `fk_device_status`) VALUES (2, NULL, '172.28.3.121', 'Cisco', 'ASA5500', 'ssh', 1, 1);

COMMIT;


-- -----------------------------------------------------
-- Data for table `ACLTrack`.`acl_type`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`acl_type` (`idacl_type`, `cat`) VALUES (1, 'ACL_Name');
INSERT INTO `ACLTrack`.`acl_type` (`idacl_type`, `cat`) VALUES (2, 'ACE');
INSERT INTO `ACLTrack`.`acl_type` (`idacl_type`, `cat`) VALUES (3, 'ACL');

COMMIT;


-- -----------------------------------------------------
-- Data for table `ACLTrack`.`hitcount_status`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`hitcount_status` (`idhitcount_status`, `status`) VALUES (1, 'No Change');
INSERT INTO `ACLTrack`.`hitcount_status` (`idhitcount_status`, `status`) VALUES (2, 'Changed');
INSERT INTO `ACLTrack`.`hitcount_status` (`idhitcount_status`, `status`) VALUES (3, 'Rest');

COMMIT;


-- -----------------------------------------------------
-- Data for table `ACLTrack`.`acl_error`
-- -----------------------------------------------------
START TRANSACTION;
USE `ACLTrack`;
INSERT INTO `ACLTrack`.`acl_error` (`idacl_error`, `error`) VALUES (1, 'OK');
INSERT INTO `ACLTrack`.`acl_error` (`idacl_error`, `error`) VALUES (2, 'ERROR');
INSERT INTO `ACLTrack`.`acl_error` (`idacl_error`, `error`) VALUES (3, 'Unknown');

COMMIT;

