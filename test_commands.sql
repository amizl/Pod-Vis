use cliovis;
show tables;

select * from subject_ontology order by parent_id;
select * from observation_ontology order by parent_id;
select * from collection_study;

select * from collection where id = 27;

select * from collection_query;