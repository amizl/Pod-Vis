use cliovis;

################################################################
DELETE FROM user;

INSERT INTO user (id, email, name, institution, password_hash)
 VALUES(1, 'bgottfried@som.umaryland.edu', 'Brian Gottfried', 'IGS', 'foo');

INSERT INTO user (id, email, name, institution, password_hash)
 VALUES(2, 'jorvis@gmail.com', 'Joshua Orvis', 'IGS', 'bar');

################################################################
DELETE FROM project;

INSERT INTO project (id, project_name, owner_id, is_public)
 VALUES (1, 'PPMI', 1, 1);

################################################################
DELETE FROM study;
