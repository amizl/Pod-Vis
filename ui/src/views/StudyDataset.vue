<template>
  <v-container v-if="collection" fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>menu_book</v-icon>
      <v-toolbar-title class="white--text pl-3"
        >Study Dataset Overview
        <div class="subtitle-1">Dataset: {{ collection.label }}</div>
      </v-toolbar-title>
      <v-spacer></v-spacer>
      <v-tooltip bottom color="primary">
        <template v-slot:activator="{ on: tooltip }">
          <v-btn color="primary--text" @click="goBack()" v-on="{ ...tooltip }">
            <v-icon left>library_books</v-icon>
            Saved Study Datasets
          </v-btn>
        </template>
        <span>Return to Saved Study Datasets</span>
      </v-tooltip>
    </v-app-bar>

    <!-- Title, Creation Date -->
    <v-sheet color="white" class="scroll rounded-lg shadow my-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Overview
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <!-- Title and description -->
            <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-card flat class="rounded-lg shadow">
                    <v-card-text>
                      <p><span>Name:</span> {{ collection.label }}</p>
                      <p><span>Created by:</span> {{ collection.user_name }}</p>
                      <p>
                        <span>Created on:</span>
                        {{ collection.date_generated_epoch | formatDate }}
                      </p>
                      <p>
                        <span>Public dataset:</span>
                        {{ collection.is_public ? 'yes' : 'no' }}
                      </p>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>

    <!-- Included Datasets -->
    <v-sheet color="white" class="scroll rounded-lg shadow my-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Source Datasets ({{ collection.studies.length }})
                <v-spacer />
                <v-toolbar-items>
                  <v-icon
                    v-if="datasets_expanded"
                    @click="datasets_expanded = false"
                    >expand_less</v-icon
                  >
                  <v-icon v-else @click="datasets_expanded = true"
                    >expand_more</v-icon
                  >
                </v-toolbar-items>
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container
        v-show="datasets_expanded"
        fluid
        fill-width
        class="ma-0 pa-0 pt-2"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <v-card flat class="rounded-lg shadow">
                    <v-card-text>
                      <p v-for="s in collection.studies">
                        <span class="font-weight-bold">{{
                          s.study.study_name
                        }}</span>
                        - {{ s.study.description }}
                      </p>
                    </v-card-text>
                  </v-card>
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>

    <!-- Demographic/Subject Variables -->
    <v-sheet color="white" class="scroll rounded-lg shadow my-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Demographic Variables ({{
                  collection.subject_variables.length
                }})
                <v-spacer />
                <v-toolbar-items>
                  <v-icon
                    v-if="demo_vars_expanded"
                    @click="demo_vars_expanded = false"
                    >expand_less</v-icon
                  >
                  <v-icon v-else @click="demo_vars_expanded = true"
                    >expand_more</v-icon
                  >
                </v-toolbar-items>
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container
        v-show="demo_vars_expanded"
        fluid
        fill-width
        class="ma-0 pa-0 pt-2"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <simple-variable-table
                    :variables="sortScales([...collection.subject_variables])"
                    dense
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>

    <!-- Observation Variables -->
    <v-sheet color="white" class="scroll rounded-lg shadow my-2">
      <v-container fluid fill-width class="ma-0 pa-0">
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-card color="#eeeeee" class="pt-1">
              <v-card-title class="primary--text pl-3 py-2"
                >Observation Variables ({{
                  collection.observation_variables.length
                }})
                <v-spacer />
                <v-toolbar-items>
                  <v-icon
                    v-if="obs_vars_expanded"
                    @click="obs_vars_expanded = false"
                    >expand_less</v-icon
                  >
                  <v-icon v-else @click="obs_vars_expanded = true"
                    >expand_more</v-icon
                  >
                </v-toolbar-items>
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>

      <v-container
        v-show="obs_vars_expanded"
        fluid
        fill-width
        class="ma-0 pa-0 pt-2"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
                <v-col cols="12" class="ma-0 pa-0">
                  <simple-variable-table
                    :variables="
                      sortScales([...collection.observation_variables])
                    "
                    dense
                  />
                </v-col>
              </v-row>
            </v-container>
          </v-col>
        </v-row>
      </v-container>
    </v-sheet>

    <!-- Cohorts -->
    <v-container fluid fill-width class="ma-0 pa-0 pt-2">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <cohort-table
            :title="'Cohorts (' + collection.cohorts.length + ')'"
            :cohorts="collection.cohorts"
          />
        </v-col>
      </v-row>
    </v-container>
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import axios from 'axios';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';
import CohortTable from '@/components/common/CohortTable.vue';
import SimpleVariableTable from '@/components/DatasetManager/SimpleVariableTable.vue';
import { sortScales } from '@/utils/helpers';

export default {
  filters: {
    formatDate(ts) {
      // note that toISOString is going to give us UTC
      return new Date(ts).toISOString().substr(0, 10);
    },
  },
  components: {
    CohortTable,
    LoadingSpinner,
    SimpleVariableTable,
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
      datasets_expanded: true,
      demo_vars_expanded: true,
      obs_vars_expanded: true,
      sortScales: sortScales,
    };
  },
  computed: {
    ...mapState('datasetManager', {
      collection: state.COLLECTION,
    }),
  },
  async created() {
    await this.fetchCollection(this.id);
  },
  methods: {
    ...mapActions('datasetManager', {
      fetchCollection: actions.FETCH_COLLECTION,
    }),
    goBack() {
      this.$router.go(-1);
    },
  },
};
</script>

<style scoped></style>
