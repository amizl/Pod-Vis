CREATE SCHEMA IF NOT EXISTS cliovis DEFAULT CHARACTER SET utf8;
USE cliovis;

DROP TABLE IF EXISTS cliovis.user ;

CREATE TABLE IF NOT EXISTS cliovis.user (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  email VARCHAR(120) NOT NULL,
  name VARCHAR(120) NOT NULL,
  institution VARCHAR(120) NULL DEFAULT NULL,
  password_hash VARCHAR(128) NOT NULL,
  UNIQUE INDEX email (email ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


DROP TABLE IF EXISTS cliovis.project ;

CREATE TABLE IF NOT EXISTS cliovis.project (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  project_name VARCHAR(45) NULL DEFAULT NULL,
  description TEXT NULL DEFAULT NULL,
  user_id INT NULL,
  project_url TEXT(1000) NULL,
  is_public TINYINT(1) NULL,
  UNIQUE INDEX project_name_UNIQUE (project_name ASC),
  INDEX fk_project_user_idx (user_id ASC),
  CONSTRAINT fk_project_user
    FOREIGN KEY (user_id)
    REFERENCES cliovis.user (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


DROP TABLE IF EXISTS cliovis.study ;

CREATE TABLE IF NOT EXISTS cliovis.study (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  study_name VARCHAR(45) NULL DEFAULT NULL,
  description TEXT NULL DEFAULT NULL,
  project_id INT NOT NULL,
  UNIQUE INDEX study_name_UNIQUE (study_name ASC),
  INDEX fk_study_project1_idx (project_id ASC),
  CONSTRAINT fk_study_project1
    FOREIGN KEY (project_id)
    REFERENCES cliovis.project (id)
    ON DELETE CASCADE
    ON UPDATE NO ACTION)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


DROP TABLE IF EXISTS cliovis.subject ;

CREATE TABLE IF NOT EXISTS cliovis.subject (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  study_id INT NOT NULL,
  subject_num VARCHAR(45) NOT NULL,
  UNIQUE INDEX subject_num_UNIQUE (subject_num ASC, study_id ASC),
  INDEX study_id_idx (study_id ASC),
  CONSTRAINT study_id
    FOREIGN KEY (study_id)
    REFERENCES cliovis.study (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


DROP TABLE IF EXISTS cliovis.subject_visit ;

CREATE TABLE IF NOT EXISTS cliovis.subject_visit (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  visit_event VARCHAR(45) NULL DEFAULT NULL,
  visit_num INT NULL DEFAULT NULL,
  disease_status VARCHAR(45) NULL DEFAULT NULL,
  event_date DATE NULL DEFAULT NULL,
  subject_id INT NOT NULL,
  UNIQUE INDEX visit_num_UNIQUE (visit_num ASC, subject_id ASC),
  INDEX fk_subject_visit_subject1_idx (subject_id ASC),
  CONSTRAINT fk_subject_visit_subject1
    FOREIGN KEY (subject_id)
    REFERENCES cliovis.subject (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;


DROP TABLE IF EXISTS cliovis.subject_ontology ;

CREATE TABLE IF NOT EXISTS cliovis.subject_ontology (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  label VARCHAR(255) NOT NULL,
  parent_id INT NULL,
  INDEX fk_subject_ontology_subject_ontology1_idx (parent_id ASC),
  CONSTRAINT fk_subject_ontology_subject_ontology1
    FOREIGN KEY (parent_id)
    REFERENCES cliovis.subject_ontology (id)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table cliovis.subject_attribute
-- -----------------------------------------------------
DROP TABLE IF EXISTS cliovis.subject_attribute ;

CREATE TABLE IF NOT EXISTS cliovis.subject_attribute (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  subject_id INT NOT NULL,
  subject_ontology_id INT NOT NULL,
  value VARCHAR(255) NOT NULL,
  value_type ENUM('int', 'string', 'date') not null,
  INDEX fk_subject_attribute_subject1_idx (subject_id ASC),
  INDEX fk_subject_attribute_subject_ontology1_idx (subject_ontology_id ASC),
  CONSTRAINT fk_subject_attribute_subject1
    FOREIGN KEY (subject_id)
    REFERENCES cliovis.subject (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_subject_attribute_subject_ontology1
    FOREIGN KEY (subject_ontology_id)
    REFERENCES cliovis.subject_ontology (id)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.collection ;

CREATE TABLE IF NOT EXISTS cliovis.collection (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  label VARCHAR(255) NOT NULL,
  date_generated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  is_public TINYINT(1) NOT NULL DEFAULT 0,
  instantiation_type ENUM('static', 'dynamic') NOT NULL,
  last_modified TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX fk_collection_user1_idx (user_id ASC),
  CONSTRAINT fk_collection_user1
    FOREIGN KEY (user_id)
    REFERENCES cliovis.user (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.collection_study ;

CREATE TABLE IF NOT EXISTS cliovis.collection_study (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  collection_id INT NOT NULL,
  study_id INT NOT NULL,
  INDEX fk_collection_study_study1_idx (study_id ASC),
  INDEX fk_collection_study_collection1_idx (collection_id ASC),
  CONSTRAINT fk_collection_study_collection1
    FOREIGN KEY (collection_id)
    REFERENCES cliovis.collection (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_collection_study_study1
    FOREIGN KEY (study_id)
    REFERENCES cliovis.study (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


-- -----------------------------------------------------
-- Table cliovis.collection_query
-- -----------------------------------------------------
DROP TABLE IF EXISTS cliovis.collection_query ;

CREATE TABLE IF NOT EXISTS cliovis.collection_query (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  collection_id INT NOT NULL,
  param VARCHAR(255) NOT NULL,
  operator VARCHAR(10) NOT NULL,
  value VARCHAR(255) NOT NULL,
  INDEX fk_collection_query_collection1_idx (collection_id ASC),
  CONSTRAINT fk_collection_query_collection1
    FOREIGN KEY (collection_id)
    REFERENCES cliovis.collection (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.cohort ;

CREATE TABLE IF NOT EXISTS cliovis.cohort (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  user_id INT NOT NULL,
  date_generated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  label VARCHAR(255) NOT NULL,
  instantiation_type ENUM('static', 'dynamic') NOT NULL,
  last_modified TIMESTAMP ON UPDATE CURRENT_TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  INDEX fk_cohort_user1_idx (user_id ASC),
  CONSTRAINT fk_cohort_user1
    FOREIGN KEY (user_id)
    REFERENCES cliovis.user (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.cohort_subject ;

CREATE TABLE IF NOT EXISTS cliovis.cohort_subject (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  cohort_id INT NOT NULL,
  subject_id INT NOT NULL,
  INDEX fk_cohort_subject_cohort1_idx (cohort_id ASC),
  INDEX fk_cohort_subject_subject1_idx (subject_id ASC),
  CONSTRAINT fk_cohort_subject_cohort1
    FOREIGN KEY (cohort_id)
    REFERENCES cliovis.cohort (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_cohort_subject_subject1
    FOREIGN KEY (subject_id)
    REFERENCES cliovis.subject (id)
    ON DELETE NO ACTION
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.cohort_query ;

CREATE TABLE IF NOT EXISTS cliovis.cohort_query (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  cohort_id INT NOT NULL,
  param VARCHAR(255) NOT NULL,
  operator VARCHAR(10) NOT NULL,
  value VARCHAR(255) NOT NULL,
  INDEX fk_cohort_query_cohort1_idx (cohort_id ASC),
  CONSTRAINT fk_cohort_query_cohort1
    FOREIGN KEY (cohort_id)
    REFERENCES cliovis.cohort (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;



DROP TABLE IF EXISTS cliovis.collection_subject_variable ;

CREATE TABLE IF NOT EXISTS cliovis.collection_subject_variable (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  collection_id INT NOT NULL,
  subject_ontology_id INT NOT NULL,
  INDEX collection_id (collection_id ASC),
  CONSTRAINT fk_collection_subject_variable_collection1
    FOREIGN KEY (collection_id)
    REFERENCES cliovis.collection (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT subject_ontology_id
    FOREIGN KEY (subject_ontology_id)
    REFERENCES cliovis.subject_ontology (id)
  )
ENGINE = InnoDB;



DROP TABLE IF EXISTS cliovis.observation_ontology ;

CREATE TABLE IF NOT EXISTS cliovis.observation_ontology (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  label VARCHAR(255) NULL,
  parent_id INT NULL DEFAULT NULL,
  CONSTRAINT fk_observation_ontology_observaton_ontology1
    FOREIGN KEY (parent_id)
    REFERENCES cliovis.observation_ontology (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;


DROP TABLE IF EXISTS cliovis.observation ;

CREATE TABLE IF NOT EXISTS cliovis.observation (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  observation_ontology_id INT NOT NULL,
  value VARCHAR(45) NULL DEFAULT NULL,
  subject_visit_id INT NOT NULL,
  value_type ENUM('int', 'string', 'date') not null,
  UNIQUE INDEX subject_visit_id_UNIQUE (subject_visit_id ASC, observation_ontology_id ASC),
  INDEX fk_observation__subject_visit_id_idx (subject_visit_id ASC),
  CONSTRAINT fk_observations_subject_visit1
    FOREIGN KEY (subject_visit_id)
    REFERENCES cliovis.subject_visit (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_observation_ontology1
    FOREIGN KEY (observation_ontology_id)
    REFERENCES cliovis.observation_ontology (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8;

DROP TABLE IF EXISTS cliovis.collection_observation_variable ;

CREATE TABLE IF NOT EXISTS cliovis.collection_observation_variable (
  id INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
  collection_id INT NOT NULL,
  observation_ontology_id INT NOT NULL,
  INDEX collection_id (collection_id ASC),
  CONSTRAINT fk_collection_obs_var_collection1
    FOREIGN KEY (collection_id)
    REFERENCES cliovis.collection (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT fk_collection_obs_var_observation_ontology1
    FOREIGN KEY (observation_ontology_id)
    REFERENCES cliovis.observation_ontology (id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
  )
ENGINE = InnoDB;



INSERT INTO user
  (email, name, institution, password_hash)
VALUES('admin@localhost', 'Admin', 'IGS', '$2b$12$NA6jDd9UtzjiFKJG/Ts94.8uHVRTLcU8LqdDklgCQfj5ikXRcPEka');

INSERT INTO project
  (project_name, description, user_id, project_url, is_public)
VALUES
  ("Parkinson's Progression Markers Initiative", "The Parkinson's Progression Markers Initiative (PPMI) is a landmark observational clinical study to comprehensively evaluate cohorts of significant interest using advanced imaging, biologic sampling and clinical and behavioral assessments to identify biomarkers of Parkinson's disease progression.", 1, "http://www.ppmi-info.org/", 1);
