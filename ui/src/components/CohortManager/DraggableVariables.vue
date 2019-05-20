<template>
  <!-- <loading-spinner v-if="isLoading" />
  <v-card v-else> -->
  <v-card>
    <v-card-title card color="white"
      ><span class="title">Variables</span>
    </v-card-title>
    <!--<v-card-text>
       <v-treeview
        :items="[...subjectVariables, ...observationVariables]"
        item-text="label"
        open-all
        transition
      > -->
    <!-- <template v-slot:label="{ item, open }">
          <div>
            <draggable :list="[item]">
              <v-chip v-for="i in [item]" :key="i.name"> {{ item.name }} </v-chip>
            </draggable>
          </div>
        </template> -->
    <!-- </v-treeview> -->
    <!-- </v-card-text> -->
    <v-list>
      <v-list-group
        v-for="subjectVariable in subjectVariables"
        :key="subjectVariable.id"
      >
        <template v-slot:activator>
          <v-list-tile>
            <v-list-tile-title>{{ subjectVariable.label }}</v-list-tile-title>
          </v-list-tile>
        </template>
        <draggable
          :list="subjectVariable.children"
          group="variables"
          handle=".handle"
          @start="dragging = true"
          @end="dragging = false"
        >
          <v-list-tile
            v-for="childVariable in subjectVariable.children"
            :key="childVariable.label"
          >
            <v-list-tile-content>
              <v-chip class="handle" outline color="blue">
                <!-- <v-avatar>
                  <v-icon color="blue">account_circle</v-icon>
                </v-avatar> -->
                {{ childVariable.label }}
              </v-chip>
            </v-list-tile-content>
          </v-list-tile>
        </draggable>
      </v-list-group>
      <v-list-group
        v-for="observationVariable in observationVariables"
        :key="observationVariable.id"
      >
        <template v-slot:activator>
          <v-list-tile>
            <v-list-tile-title>{{
              observationVariable.label
            }}</v-list-tile-title>
          </v-list-tile>
        </template>
        <draggable
          :list="observationVariable.children"
          group="variables"
          handle=".handle"
          @start="dragging = true"
          @end="dragging = false"
        >
          <v-list-tile
            v-for="childVariable in observationVariable.children"
            :key="childVariable.label"
          >
            <v-list-tile-content>
              <v-chip class="handle" outline color="green">
                <!-- <v-avatar>
                  <v-icon color="green">insert_chart</v-icon>
                </v-avatar> -->
                {{ childVariable.label }}
              </v-chip>
            </v-list-tile-content>
          </v-list-tile>
        </draggable>
      </v-list-group>
    </v-list>
  </v-card>
</template>

<script>
import draggable from "vuedraggable";
import { uniqBy } from "lodash";
import { mapState } from "vuex";
import { state } from "@/store/modules/cohortManager/types";

export default {
  components: {
    draggable
  },
  data: () => ({
    dragging: false,
    hovering: false,
    observationVariables: [],
    subjectVariables: []
  }),
  computed: {
    ...mapState("cohortManager", {
      collection: state.COLLECTION,
      isLoading: state.IS_LOADING
    })
  },
  watch: {
    collection() {
      // const subjectVariables = this.makeH ierarchy(
      //   this.collection.subject_variables.map(variable => ({
      //     ...variable,
      //     type: 'subject',
      //   }))
      // );

      const subjectVariables = this.makeHierarchy(
        this.collection.subject_variables
      );
      subjectVariables.forEach(subjectVariable => {
        subjectVariable.children.forEach(child => (child["type"] = "subject"));
      });

      const observationVariables = this.makeHierarchy(
        this.collection.observation_variables
      );

      observationVariables.forEach(observationVariable => {
        observationVariable.children.forEach(
          child => (child["type"] = "observation")
        );
      });

      this.subjectVariables = subjectVariables;
      this.observationVariables = observationVariables;
    }
  },
  async created() {
    // console.log(this.collection.observation_variables);
    // console.log(this.collection.subject_variables);
    // fetch the shared input and output variables for collection
    // and assign them to variables...
  },
  methods: {
    fetchVariables() {
      // fetch the shared input and output variables for collection
    },
    makeHierarchy(data) {
      const ontologies = data.map(obs => obs.ontology);
      const parents = uniqBy(
        ontologies.map(ontology => ontology.parent),
        "label"
      ).map(parent => ({
        ...parent,
        children: ontologies.filter(
          ontology => ontology.parent.label === parent.label
        )
      }));
      return parents;
    }
  }
};
</script>

<style scoped>
.grab {
  cursor: grab;
}
</style>
