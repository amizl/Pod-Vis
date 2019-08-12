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

export function getInputVariablesFromQueries(queries, inputVariables) {
  return Object.keys(queries).map(variable => {
    return {
      query: queries[variable],
      variable: inputVariables.find(inputVar => {
        const { label, type } = inputVar;
        if (type === 'study' || type === 'subject') {
          return label === variable;
        } else {
          // type is 'observation'
          const { parentLabel } = inputVar;
          const obsLabel = `${parentLabel} - ${label}`;
          return obsLabel === variable;
        }
      }),
    };
  });
}
