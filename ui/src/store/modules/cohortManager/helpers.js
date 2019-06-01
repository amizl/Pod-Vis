import { uniqBy } from 'lodash';

export function makeHierarchy(data) {
  const ontologies = data.map(obs => obs.ontology);
  const parents = uniqBy(
    ontologies.map(ontology => ontology.parent),
    'label'
  ).map(parent => ({
    ...parent,
    children: ontologies.filter(
      ontology => ontology.parent.label === parent.label
    ),
  }));
  return parents;
}
