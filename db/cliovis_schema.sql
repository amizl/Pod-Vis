-- MySQL Script generated by MySQL Workbench
-- Thu 14 Mar 2019 11:17:06 PM CDT
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

-- -----------------------------------------------------
-- Schema mydb
-- -----------------------------------------------------
-- -----------------------------------------------------
-- Schema cliovis
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema cliovis
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `cliovis` DEFAULT CHARACTER SET utf8 ;
USE `cliovis` ;

-- -----------------------------------------------------
-- Table `cliovis`.`observations`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`observations` (
  `observation_id` INT(11) NOT NULL AUTO_INCREMENT,
  `item` VARCHAR(45) NOT NULL,
  `value` VARCHAR(45) NULL DEFAULT NULL,
  `category` VARCHAR(45) NULL DEFAULT NULL,
  `scale` VARCHAR(45) NOT NULL,
  `subject_visit_id` INT(11) NOT NULL,
  `item_type` VARCHAR(45) NULL DEFAULT NULL,
  PRIMARY KEY (`observation_id`),
  UNIQUE INDEX `subject_visit_id_UNIQUE` (`subject_visit_id` ASC, `item` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`user`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`user` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `email` VARCHAR(120) NOT NULL,
  `name` VARCHAR(120) NOT NULL,
  `institution` VARCHAR(120) NULL DEFAULT NULL,
  `password_hash` VARCHAR(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `email` (`email` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`project`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`project` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `project_name` VARCHAR(45) NULL DEFAULT NULL,
  `description` VARCHAR(100) NULL DEFAULT NULL,
  `owner_id` INT NULL,
  `project_url` TEXT(1000) NULL,
  `is_public` TINYINT(1) NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `project_name_UNIQUE` (`project_name` ASC),
  INDEX `fk_project_user_idx` (`owner_id` ASC),
  CONSTRAINT `fk_project_user`
    FOREIGN KEY (`owner_id`)
    REFERENCES `cliovis`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`study`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`study` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `study_name` VARCHAR(45) NULL DEFAULT NULL,
  `description` VARCHAR(100) NULL DEFAULT NULL,
  `project_id` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `study_name_UNIQUE` (`study_name` ASC),
  INDEX `fk_study_project1_idx` (`project_id` ASC),
  CONSTRAINT `fk_study_project1`
    FOREIGN KEY (`project_id`)
    REFERENCES `cliovis`.`project` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`subject`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`subject` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `study_id` INT(11) NOT NULL,
  `subject_num` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `subject_num_UNIQUE` (`subject_num` ASC, `study_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`subject_visit`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`subject_visit` (
  `visit_id` INT(11) NOT NULL AUTO_INCREMENT,
  `visit_event` VARCHAR(45) NULL DEFAULT NULL,
  `visit_num` INT(11) NULL DEFAULT NULL,
  `disease_status` VARCHAR(45) NULL DEFAULT NULL,
  `event_date` DATE NULL DEFAULT NULL,
  `subject_id` INT(11) NOT NULL,
  PRIMARY KEY (`visit_id`),
  UNIQUE INDEX `visit_num_UNIQUE` (`visit_num` ASC, `subject_id` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


-- -----------------------------------------------------
-- Table `cliovis`.`subject_ontology`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`subject_ontology` (
  `id` INT NOT NULL,
  `label` VARCHAR(255) NOT NULL,
  `parent_id` INT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_subject_ontology_subject_ontology1_idx` (`parent_id` ASC),
  CONSTRAINT `fk_subject_ontology_subject_ontology1`
    FOREIGN KEY (`parent_id`)
    REFERENCES `cliovis`.`subject_ontology` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cliovis`.`subject_attribute`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`subject_attribute` (
  `id` INT NOT NULL,
  `subject_id` INT(11) NOT NULL,
  `subject_ontology_id` INT NOT NULL,
  `value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_subject_attribute_subject1_idx` (`subject_id` ASC),
  INDEX `fk_subject_attribute_subject_ontology1_idx` (`subject_ontology_id` ASC),
  CONSTRAINT `fk_subject_attribute_subject1`
    FOREIGN KEY (`subject_id`)
    REFERENCES `cliovis`.`subject` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_subject_attribute_subject_ontology1`
    FOREIGN KEY (`subject_ontology_id`)
    REFERENCES `cliovis`.`subject_ontology` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cliovis`.`collection`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`collection` (
  `id` INT NOT NULL,
  `creator_id` INT(11) NOT NULL,
  `label` VARCHAR(255) NOT NULL,
  `date_generated` DATETIME NULL,
  `is_public` TINYINT(1) NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`),
  INDEX `fk_collection_user1_idx` (`creator_id` ASC),
  CONSTRAINT `fk_collection_user1`
    FOREIGN KEY (`creator_id`)
    REFERENCES `cliovis`.`user` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cliovis`.`collection_study`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`collection_study` (
  `id` INT NOT NULL,
  `collection_id` INT NOT NULL,
  `study_id` INT(11) NOT NULL,
  INDEX `fk_collection_study_collection1_idx` (`collection_id` ASC),
  INDEX `fk_collection_study_study1_idx` (`study_id` ASC),
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_collection_study_collection1`
    FOREIGN KEY (`collection_id`)
    REFERENCES `cliovis`.`collection` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_collection_study_study1`
    FOREIGN KEY (`study_id`)
    REFERENCES `cliovis`.`study` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table `cliovis`.`collection_query`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `cliovis`.`collection_query` (
  `id` INT NOT NULL,
  `collection_id` INT NOT NULL,
  `param` VARCHAR(255) NOT NULL,
  `operator` VARCHAR(10) NOT NULL,
  `value` VARCHAR(255) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `fk_collection_query_collection1_idx` (`collection_id` ASC),
  CONSTRAINT `fk_collection_query_collection1`
    FOREIGN KEY (`collection_id`)
    REFERENCES `cliovis`.`collection` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
