<template>
  <v-container v-if="collection" fluid fill-width class="ma-0 pa-2">
    <v-app-bar app class="primary">
      <v-icon color="white" large>menu_book</v-icon>
      <v-toolbar-title class="white--text pl-3"
		       >Study Dataset Overview
        <div class="subtitle-1">Dataset: {{ collection.label }}</div>
      </v-toolbar-title
      >
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
                      <p><span>Created on:</span> {{ collection.date_generated_epoch | formatDate }}</p>
		      <p><span>Public dataset:</span> {{ collection.is_public ? "yes" : "no" }}</p>
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
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
      
      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
	<v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
	    
	    <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
		<v-col cols="12" class="ma-0 pa-0">
                  <v-card flat class="rounded-lg shadow">
                    <v-card-text>
		      <p v-for="s in collection.studies">{{s.study.study_name}} - {{s.study.description}}</p>
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
			    >Demographic Variables ({{ collection.subject_variables.length }})
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
      
      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
	<v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
	    
	    <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
		<v-col cols="12" class="ma-0 pa-0">
                  <v-card flat class="rounded-lg shadow">
                    <v-card-text>
                    </v-card-text>
                  </v-card>
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
			    >Observation Variables ({{ collection.observation_variables.length }})
              </v-card-title>
            </v-card>
          </v-col>
        </v-row>
      </v-container>
      
      <v-container fluid fill-width class="ma-0 pa-0 pt-2">
	<v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
	    
	    <v-container fluid fill-width class="ma-0 pa-0 pt-0">
              <v-row class="ma-0 pa-0">
		<v-col cols="12" class="ma-0 pa-0">
                  <v-card flat class="rounded-lg shadow">
                    <v-card-text>
                    </v-card-text>
                  </v-card>
		</v-col>
              </v-row>
            </v-container>
	    
          </v-col>
	</v-row>
      </v-container>
    </v-sheet>

        <!--

          <v-container fluid fill-width class="ma-0 pa-0 pt-2">
            <v-row class="ma-0 pa-0">
              <v-col cols="12" class="ma-0 pa-0">
                <v-card flat class="rounded-lg shadow pt-2">
                  <v-card-title primary-title card color="white">
                    <span class="title">Variables</span>
                  </v-card-title>
                  <variable-table :dataset-id="id" />
                </v-card>
              </v-col>
            </v-row>
          </v-container>
        </v-col>

        <v-col cols="4" class="ma-0 pa-0 pl-2">
          <v-card flat class="rounded-lg shadow">
            <v-card-title primary-title card color="white">
              <span class="title">Subject Summary</span>
            </v-card-title>
            <v-card-text v-if="summaryData">
              <sunburst-chart
                :data="summaryData"
                :keyorder="groupBy"
                :color="{ male: '#00AEEF', female: '#EC76BC' }"
              >
                <template
                  v-slot:legend="{ data, color, colorScale, actions, nodes }"
                >
                  <sunburst-legend
                    :data="data"
                    :color-scale="colorScale"
                    :color="color"
                    :actions="actions"
                    :nodes="nodes"
                  ></sunburst-legend>
                </template>
              </sunburst-chart>
            </v-card-text>
            <v-card-text v-else>
              <loading-spinner medium class="ma-5" />
            </v-card-text>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
    -->
    
  </v-container>
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import axios from 'axios';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';
import LoadingSpinner from '@/components/common/LoadingSpinner.vue';

export default {
  filters: {
    formatDate(ts) {
      // note that toISOString is going to give us UTC
      return new Date(ts).toISOString().substr(0, 10);
    },
  },
  components: {
    VariableTable,
    LoadingSpinner,
  },
  props: {
    id: {
      type: Number,
      required: true,
    },
  },
  data() {
    return {
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
