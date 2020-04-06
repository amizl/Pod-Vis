<template>
  <div>
    <v-treeview
      v-model="selectedSubjectVariables"
      color="primary"
      return-object
      selectable
      :search="search"
      :open="openSubj"
      :items="
        [
          { type: 'study', id: 24, label: 'Dataset', parent_id: null },
          ...subjectVariables,
        ].sort(function(a, b) {
          return a.label < b.label ? -1 : a.label > b.label ? 1 : 0;
        })
      "
      item-text="label"
    ></v-treeview>
    <v-treeview
      v-model="selectedObservationVariables"
      color="primary"
      selectable
      return-object
      :items="observationVariables"
      :search="search"
      :open="openObs"
      item-text="label"
    ></v-treeview>
  </div>
</template>

<script>
import { actions, state, getters } from '@/store/modules/cohortManager/types';
import { mapActions, mapState, mapGetters } from 'vuex';
import { uniqBy } from 'lodash';

var indexVars = function(dict, vars) {
  vars.forEach(v => {
    dict[v.id] = v;
    if (v.children) {
      indexVars(dict, v.children);
    }
  });
};

export default {
  props: {
    search: {
      type: String,
      default: '',
    },
  },
  data: () => ({
    selectedSubjectVariables: [],
    selectedObservationVariables: [],
    dragging: false,
    hovering: false,
    observationVariables: [],
    observationVariablesD: {},
    subjectVariables: [],
    subjectVariablesD: {},
    propagateChanges: false,
    openSubj: [],
    openObs: [],
  }),
  computed: {
    ...mapGetters('cohortManager', {
      hasUserSelectedCohort: getters.HAS_USER_SELECTED_COHORT,
    }),
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      vars: state.INPUT_VARIABLES,
      cohort: state.COHORT,
    }),
  },
  watch: {
    cohort() {
      // pull vars from user-selected cohort
      if (this.hasUserSelectedCohort) {
        this.selectedSubjectVariables = this.vars.filter(
          variable => variable.type === 'subject'
        );
        this.selectedObservationVariables = this.vars.filter(
          variable => variable.type === 'observation'
        );
      }
      // otherwise reset selections
      else {
        this.selectedSubjectVariables = [];
        this.selectedObservationVariables = [];
      }
      // const observationVariables = newCohort.input_variables
      //   .filter(variable => variable.observation_ontology !== null)
      //   .map(variable => variable.observation_ontology.id);
    },
    observationVariables(newObsVars) {
      // index by id
      this.observationVariablesD = {};
      indexVars(this.observationVariablesD, newObsVars);
    },
    subjectVariables(newSubjVars) {
      // index by id
      this.subjectVariablesD = {};
      indexVars(this.subjectVariablesD, newSubjVars);
    },
    selectedSubjectVariables(newSubjectVariables) {
      var ivt = this;

      new Promise(function(resolve, reject) {
        // open up any selected nodes that are not already open
        var openIds = {};
        ivt.openSubj.forEach(s => {
          openIds[s.id] = true;
        });
        newSubjectVariables.forEach(s => {
          if (!(s.id in openIds)) {
            if (s.children) {
              ivt.openSubj.push(s);
              openIds[s.id] = true;
            }
            if (s.parent && !(s.parent.id in openIds)) {
              ivt.openSubj.push(s.parent);
              openIds[s.parent.id] = true;
            }
          }
        });

        // slight delay on actually adding the variables so that the
        // dialog/tree has time to update first
        setTimeout(() => {
          ivt.subjectVariablesChanged(newSubjectVariables);
          resolve();
        }, 100);
      });
    },
    selectedObservationVariables(newObservationVariables) {
      var ivt = this;

      new Promise(function(resolve, reject) {
        // open up any selected nodes that are not already open
        var openIds = {};
        ivt.openObs.forEach(s => {
          openIds[s.id] = true;
        });
        newObservationVariables.forEach(s => {
          if (!(s.id in openIds)) {
            if (s.children) {
              ivt.openObs.push(s);
              openIds[s.id] = true;
            }
            if (s.parent && !(s.parent.id in openIds)) {
              ivt.openObs.push(s.parent);
              openIds[s.parent.id] = true;
            }

            if (s.parentID && !(s.parentID in openIds)) {
              ivt.openObs.push(ivt.observationVariablesD[s.parentID]);
              openIds[s.parentID] = true;
            }
          }
        });

        // slight delay on actually adding the variables so that the
        // dialog/tree has time to update first
        setTimeout(() => {
          ivt.observationVariablesChanged(newObservationVariables);
          resolve();
        }, 100);
      });
    },
  },
  async created() {
    this.subjectVariables = this.collection.subject_variables;
    this.observationVariables = this.collection.observation_variables;
  },
  methods: {
    ...mapActions('cohortManager', {
      setInputVariables: actions.SET_INPUT_VARIABLES,
    }),
    makeHierarchy(data) {
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
    },
    subjectVariablesChanged(newSubjectVariables) {
      if (this.propagateChanges) {
        this.setInputVariables([
          // Filter parent nodes because we don't want them added to our list,
          // i.e, 'Demographics'
          ...newSubjectVariables.filter(variable => !variable.children),
          ...this.selectedObservationVariables.filter(
            variable => !variable.children
          ),
        ]);
      }
    },
    observationVariablesChanged(newObservationVariables) {
      if (this.propagateChanges) {
        this.setInputVariables([
          ...this.selectedSubjectVariables.filter(
            variable => !variable.children
          ),
          ...newObservationVariables.filter(variable => !variable.children),
        ]);
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
