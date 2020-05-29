-- MySQL dump 10.13  Distrib 5.7.24, for macos10.14 (x86_64)
--
-- Host: localhost    Database: cliovis
-- ------------------------------------------------------
-- Server version	5.7.24

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Current Database: `cliovis`
--

CREATE DATABASE /*!32312 IF NOT EXISTS*/ `cliovis` /*!40100 DEFAULT CHARACTER SET utf8 */;

USE `cliovis`;

--
-- Table structure for table `cohort`
--

DROP TABLE IF EXISTS `cohort`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cohort` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `collection_id` int(11) NOT NULL,
  `date_generated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `label` varchar(255) NOT NULL,
  `instantiation_type` enum('static','dynamic') NOT NULL,
  `last_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_cohort_user1_idx` (`user_id`),
  KEY `fk_cohort_collection1` (`collection_id`),
  CONSTRAINT `fk_cohort_collection1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cohort_input_variable`
--

DROP TABLE IF EXISTS `cohort_input_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cohort_input_variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cohort_id` int(11) NOT NULL,
  `study_id` int(11) DEFAULT NULL,
  `observation_ontology_id` int(11) DEFAULT NULL,
  `subject_ontology_id` int(11) DEFAULT NULL,
  `dimension_label` enum('left_y_axis','right_y_axis','roc','change') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cohort_input_cohort_idx` (`cohort_id`),
  KEY `fk_cohort_input_study1` (`study_id`),
  KEY `fk_cohort_input_observation_ontology1` (`observation_ontology_id`),
  KEY `fk_cohort_input_subject_ontology1` (`subject_ontology_id`),
  CONSTRAINT `fk_cohort_input_cohort1` FOREIGN KEY (`cohort_id`) REFERENCES `cohort` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_input_observation_ontology1` FOREIGN KEY (`observation_ontology_id`) REFERENCES `observation_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_input_study1` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_input_subject_ontology1` FOREIGN KEY (`subject_ontology_id`) REFERENCES `subject_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cohort_output_variable`
--

DROP TABLE IF EXISTS `cohort_output_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cohort_output_variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cohort_id` int(11) NOT NULL,
  `study_id` int(11) DEFAULT NULL,
  `observation_ontology_id` int(11) DEFAULT NULL,
  `subject_ontology_id` int(11) DEFAULT NULL,
  `dimension_label` enum('left_y_axis','right_y_axis','roc','change') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cohort_output_cohort_idx` (`cohort_id`),
  KEY `fk_cohort_output_study1` (`study_id`),
  KEY `fk_cohort_output_observation_ontology1` (`observation_ontology_id`),
  KEY `fk_cohort_output_subject_ontology1` (`subject_ontology_id`),
  CONSTRAINT `fk_cohort_output_cohort1` FOREIGN KEY (`cohort_id`) REFERENCES `cohort` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_output_observation_ontology1` FOREIGN KEY (`observation_ontology_id`) REFERENCES `observation_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_output_study1` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_output_subject_ontology1` FOREIGN KEY (`subject_ontology_id`) REFERENCES `subject_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cohort_query`
--

DROP TABLE IF EXISTS `cohort_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cohort_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cohort_id` int(11) NOT NULL,
  `input_variable_id` int(11) NOT NULL,
  `min_value` decimal(11,2) DEFAULT NULL,
  `max_value` decimal(11,2) DEFAULT NULL,
  `value` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cohort_query_cohort1_idx` (`cohort_id`),
  KEY `fk_cohort_query_input_variable_idx` (`input_variable_id`),
  CONSTRAINT `fk_cohort_query_cohort1` FOREIGN KEY (`cohort_id`) REFERENCES `cohort` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_query_input_variable` FOREIGN KEY (`input_variable_id`) REFERENCES `cohort_input_variable` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `cohort_subject`
--

DROP TABLE IF EXISTS `cohort_subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cohort_subject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cohort_id` int(11) NOT NULL,
  `subject_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_cohort_subject_cohort1_idx` (`cohort_id`),
  KEY `fk_cohort_subject_subject1_idx` (`subject_id`),
  CONSTRAINT `fk_cohort_subject_cohort1` FOREIGN KEY (`cohort_id`) REFERENCES `cohort` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_cohort_subject_subject1` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection`
--

DROP TABLE IF EXISTS `collection`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `label` varchar(255) NOT NULL,
  `date_generated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `is_public` tinyint(1) NOT NULL DEFAULT '0',
  `instantiation_type` enum('static','dynamic') NOT NULL,
  `last_modified` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  KEY `fk_collection_user1_idx` (`user_id`),
  CONSTRAINT `fk_collection_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=28 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection_observation_variable`
--

DROP TABLE IF EXISTS `collection_observation_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection_observation_variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collection_id` int(11) NOT NULL,
  `observation_ontology_id` int(11) NOT NULL,
  `first_visit_event` varchar(45) DEFAULT NULL,
  `last_visit_event` varchar(45) DEFAULT NULL,
  `first_visit_num` int(11) DEFAULT NULL,
  `last_visit_num` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `collection_id` (`collection_id`),
  KEY `fk_collection_obs_var_observation_ontology1` (`observation_ontology_id`),
  CONSTRAINT `fk_collection_obs_var_collection1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_collection_obs_var_observation_ontology1` FOREIGN KEY (`observation_ontology_id`) REFERENCES `observation_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=130 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection_query`
--

DROP TABLE IF EXISTS `collection_query`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection_query` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collection_id` int(11) NOT NULL,
  `param` varchar(255) NOT NULL,
  `operator` varchar(10) NOT NULL,
  `value` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_collection_query_collection1_idx` (`collection_id`),
  CONSTRAINT `fk_collection_query_collection1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection_study`
--

DROP TABLE IF EXISTS `collection_study`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection_study` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collection_id` int(11) NOT NULL,
  `study_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_collection_study_study1_idx` (`study_id`),
  KEY `fk_collection_study_collection1_idx` (`collection_id`),
  CONSTRAINT `fk_collection_study_collection1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_collection_study_study1` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=42 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `collection_subject_variable`
--

DROP TABLE IF EXISTS `collection_subject_variable`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `collection_subject_variable` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `collection_id` int(11) NOT NULL,
  `subject_ontology_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `collection_id` (`collection_id`),
  KEY `subject_ontology_id` (`subject_ontology_id`),
  CONSTRAINT `fk_collection_subject_variable_collection1` FOREIGN KEY (`collection_id`) REFERENCES `collection` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `subject_ontology_id` FOREIGN KEY (`subject_ontology_id`) REFERENCES `subject_ontology` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=50 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `events`
--

DROP TABLE IF EXISTS `events`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `events` (
  `event_id` int(11) NOT NULL,
  `event_name` varchar(45) NOT NULL,
  `subject_visit_id` int(11) NOT NULL,
  `location` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`event_id`),
  KEY `fk_events_subject_visit1_idx` (`subject_visit_id`),
  CONSTRAINT `fk_events_subject_visit1` FOREIGN KEY (`subject_visit_id`) REFERENCES `subject_visit` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `group_perms`
--

DROP TABLE IF EXISTS `group_perms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `group_perms` (
  `groups_id` int(11) NOT NULL,
  `perms_id` int(11) NOT NULL,
  PRIMARY KEY (`groups_id`,`perms_id`),
  KEY `fk_group_perms_groups1_idx` (`groups_id`),
  KEY `fk_group_perms_perms1_idx` (`perms_id`),
  CONSTRAINT `fk_group_perms_groups1` FOREIGN KEY (`groups_id`) REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_group_perms_perms1` FOREIGN KEY (`perms_id`) REFERENCES `perms` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `groups`
--

DROP TABLE IF EXISTS `groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `groups` (
  `id` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name_UNIQUE` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `observation`
--

DROP TABLE IF EXISTS `observation`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `observation` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `observation_ontology_id` int(11) NOT NULL,
  `value` varchar(45) DEFAULT NULL,
  `subject_visit_id` int(11) NOT NULL,
  `value_type` enum('int','string','date','char','decimal') NOT NULL,
  `int_value` int(11) DEFAULT NULL,
  `dec_value` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subject_visit_id_UNIQUE` (`subject_visit_id`,`observation_ontology_id`),
  KEY `fk_observation__subject_visit_id_idx` (`subject_visit_id`),
  KEY `fk_observation_ontology1` (`observation_ontology_id`),
  CONSTRAINT `fk_observation_ontology1` FOREIGN KEY (`observation_ontology_id`) REFERENCES `observation_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_observations_subject_visit1` FOREIGN KEY (`subject_visit_id`) REFERENCES `subject_visit` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=2080105 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `observation_ontology`
--

DROP TABLE IF EXISTS `observation_ontology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `observation_ontology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(255) DEFAULT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `value_type` enum('int','decimal','char','date') DEFAULT NULL,
  `data_category` enum('Categorical','Ordinal','Continuous') DEFAULT NULL,
  `flip_axis` tinyint(1) DEFAULT '0',
  PRIMARY KEY (`id`),
  KEY `fk_observation_ontology_observaton_ontology1` (`parent_id`),
  CONSTRAINT `fk_observation_ontology_observaton_ontology1` FOREIGN KEY (`parent_id`) REFERENCES `observation_ontology` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=359 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `observation_summary`
--

DROP TABLE IF EXISTS `observation_summary`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `observation_summary` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `observation_ontology_id` int(11) NOT NULL,
  `value_type` enum('int','decimal') DEFAULT NULL,
  `int_value` int(11) DEFAULT NULL,
  `dec_value` decimal(10,0) DEFAULT NULL,
  `value` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subject_id_ontology_id_UNIQUE` (`subject_id`,`observation_ontology_id`),
  KEY `fk_observation_summary_subject1_idx` (`subject_id`),
  KEY `fk_observation_summary_observation_ontology1_idx` (`observation_ontology_id`),
  CONSTRAINT `fk_observation_summary_observation_ontology1` FOREIGN KEY (`observation_ontology_id`) REFERENCES `observation_ontology` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_observation_summary_subject1` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=149601 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `perms`
--

DROP TABLE IF EXISTS `perms`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `perms` (
  `id` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `description` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `perms`
--

LOCK TABLES `perms` WRITE;
/*!40000 ALTER TABLE `perms` DISABLE KEYS */;
/*!40000 ALTER TABLE `perms` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `project`
--

DROP TABLE IF EXISTS `project`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `project` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `project_name` varchar(45) DEFAULT NULL,
  `description` text,
  `user_id` int(11) DEFAULT NULL,
  `project_url` text,
  `is_public` tinyint(1) DEFAULT NULL,
  `primary_disease` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `project_name_UNIQUE` (`project_name`),
  KEY `fk_project_user_idx` (`user_id`),
  CONSTRAINT `fk_project_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role`
--

DROP TABLE IF EXISTS `role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role` (
  `id` int(11) NOT NULL,
  `name` varchar(45) DEFAULT NULL,
  `display_name` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `role_perm`
--

DROP TABLE IF EXISTS `role_perm`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `role_perm` (
  `role_id` int(11) NOT NULL,
  `perms_id` int(11) NOT NULL,
  PRIMARY KEY (`role_id`,`perms_id`),
  KEY `fk_role_perm_role1_idx` (`role_id`),
  KEY `fk_role_perm_perms1_idx` (`perms_id`),
  CONSTRAINT `fk_role_perm_perms1` FOREIGN KEY (`perms_id`) REFERENCES `perms` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_role_perm_role1` FOREIGN KEY (`role_id`) REFERENCES `role` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `study`
--

DROP TABLE IF EXISTS `study`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `study` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study_name` varchar(45) DEFAULT NULL,
  `description` text,
  `project_id` int(11) NOT NULL,
  `longitudinal` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `study_name_UNIQUE` (`study_name`),
  KEY `fk_study_project1_idx` (`project_id`),
  CONSTRAINT `fk_study_project1` FOREIGN KEY (`project_id`) REFERENCES `project` (`id`) ON DELETE CASCADE ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subject`
--

DROP TABLE IF EXISTS `subject`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subject` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `study_id` int(11) NOT NULL,
  `subject_num` varchar(45) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `subject_num_UNIQUE` (`subject_num`,`study_id`),
  KEY `study_id_idx` (`study_id`),
  CONSTRAINT `study_id` FOREIGN KEY (`study_id`) REFERENCES `study` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=6063 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subject_attribute`
--

DROP TABLE IF EXISTS `subject_attribute`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subject_attribute` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `subject_id` int(11) NOT NULL,
  `subject_ontology_id` int(11) NOT NULL,
  `value` varchar(255) NOT NULL,
  `value_type` enum('int','string','date','decimal','char') NOT NULL,
  `int_value` int(11) DEFAULT NULL,
  `dec_value` decimal(10,0) DEFAULT NULL,
  `date_value` date DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_subject_attribute_subject1_idx` (`subject_id`),
  KEY `fk_subject_attribute_subject_ontology1_idx` (`subject_ontology_id`),
  CONSTRAINT `fk_subject_attribute_subject1` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_subject_attribute_subject_ontology1` FOREIGN KEY (`subject_ontology_id`) REFERENCES `subject_ontology` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=25328 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subject_ontology`
--

DROP TABLE IF EXISTS `subject_ontology`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subject_ontology` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `label` varchar(255) NOT NULL,
  `parent_id` int(11) DEFAULT NULL,
  `value_type` enum('int','decimal','char','date','string') DEFAULT NULL,
  `data_category` enum('Categorical','Ordinal','Continuous') DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_subject_ontology_subject_ontology1_idx` (`parent_id`),
  CONSTRAINT `fk_subject_ontology_subject_ontology1` FOREIGN KEY (`parent_id`) REFERENCES `subject_ontology` (`id`) ON DELETE NO ACTION ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=24 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `subject_visit`
--

DROP TABLE IF EXISTS `subject_visit`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `subject_visit` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `visit_event` varchar(45) DEFAULT NULL,
  `visit_num` int(11) DEFAULT NULL,
  `disease_status` varchar(45) DEFAULT NULL,
  `event_date` date DEFAULT NULL,
  `subject_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `visit_num_UNIQUE` (`visit_num`,`subject_id`),
  KEY `fk_subject_visit_subject1_idx` (`subject_id`),
  CONSTRAINT `fk_subject_visit_subject1` FOREIGN KEY (`subject_id`) REFERENCES `subject` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=31639 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `user`
--

DROP TABLE IF EXISTS `user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(120) NOT NULL,
  `name` varchar(120) NOT NULL,
  `institution` varchar(120) DEFAULT NULL,
  `password_hash` varchar(128) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user`
--

LOCK TABLES `user` WRITE;
/*!40000 ALTER TABLE `user` DISABLE KEYS */;
INSERT INTO `user` VALUES (1,'admin@localhost','Admin','IGS','$2b$12$NA6jDd9UtzjiFKJG/Ts94.8uHVRTLcU8LqdDklgCQfj5ikXRcPEka');
/*!40000 ALTER TABLE `user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_groups`
--

DROP TABLE IF EXISTS `user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_groups` (
  `user_id` int(11) NOT NULL,
  `groups_id` int(11) NOT NULL,
  PRIMARY KEY (`user_id`,`groups_id`),
  KEY `fk_user_groups_user1_idx` (`user_id`),
  KEY `fk_user_groups_groups1_idx` (`groups_id`),
  CONSTRAINT `fk_user_groups_groups1` FOREIGN KEY (`groups_id`) REFERENCES `groups` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `fk_user_groups_user1` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-11-22 12:35:11
