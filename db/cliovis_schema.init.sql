use cliovis;

################################################################
DELETE FROM user;

INSERT INTO user (id, email, name, institution, password_hash)
 VALUES(1, 'bgottfried@som.umaryland.edu', 'Brian Gottfried', 'IGS', '$2b$12$J2TLCr02R./EwWKdeJ22UuTcRI9Sg2BGLOaM7cyKjpc3LmrzjRc5G');

INSERT INTO user (id, email, name, institution, password_hash)
 VALUES(2, 'jorvis@gmail.com', 'Joshua Orvis', 'IGS', 'bar');

################################################################
DELETE FROM project;

INSERT INTO project (project_name, description, owner_id, project_url, is_public)
VALUES ("Parkinson’s Progression Markers Initiative", "The Parkinson’s Progression Markers Initiative (PPMI) is a landmark observational clinical study to comprehensively evaluate cohorts of significant interest using advanced imaging, biologic sampling and clinical and behavioral assessments to identify biomarkers of Parkinson’s disease progression.", 1, "http://www.ppmi-info.org/", 1)

################################################################
DELETE FROM study;
