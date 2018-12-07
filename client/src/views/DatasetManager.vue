<template lang="pug">
v-container(
  fluid
  fill-height
  grid-list-xl)
  v-toolbar(app).white
    v-layout
      v-flex(xs6)
        v-text-field(
          v-model="search"
          prepend-inner-icon="search"
          label="Search for Dataset"
          solo
          flat
          background-color='secondary'
          ).mt-2
      v-flex(xs6)
    v-toolbar-items
      v-btn(
        append
        :to='selectedDatasets | buildPath'
        flat

        :disabled='selectedDatasets === null')
        v-icon(left) build
        | BUILD DATASET
      v-btn(
        @click.native.stop='createCohortSheet = !createCohortSheet'
        flat

        :disabled='selectedDatasets === null')
        v-icon(left) group_add
        | ADD TO PROFILE
      //- v-avatar(
      //-     :tile="tile"
      //-     :size="avatarSize"
      //-     color="grey lighten-4"
      //-  ).mt-2.ml-4
      //-   v-img(src='https://s.gravatar.com/avatar/368de2b2d2cf606aa1253cb8ce2d6c3a?s=80')
  v-layout(row wrap)
    //- v-flex(xs4)
    //-   filter-tree
    v-flex(xs12)
      dataset-table(:search='search')
    //- v-flex(xs6 fill-height)
      donut-chart(v-if='selectedDatasets', :data='selectedDatasets')
  // Bottom sheets triggered by toolbar
  v-bottom-sheet(v-model="createCohortSheet" inset style='overflow:scroll;')
    v-layout
      v-flex(xs12)
        v-card
          v-card-title(style='color:white' primary-title).primary
            h2 CREATE COHORT
          v-card-text.pa-4
            p Selected Datasets:
            v-chip(
              v-if='selectedDatasets'
              close
              v-for='dataset in selectedDatasets') {{ dataset.dataset }}
          v-card-text.pa-4
            p Outcome Measures
            outcome-table
          v-card-text.pa-4
            p Demographics
            demographics-table
            //- p Outcome Measures:
            //- v-treeview(:items='outcomes.PPMI')
            //- div(v-for='outcome in outcomes.PPMI')
            //-   p {{ outcome.name }}:
            //-     v-chip(v-for='child in outcome.children') {{ child.name}}
          //- v-card-text.pa-4
            p Variables:
            v-chip(v-if='selectedDatasets' v-for='outcome in outcomeMeasures') {{ outcome }}
          v-card-actions.pa-4
            v-text-field(
              prepend-icon='create'
              label="Synthetic Cohort Name"
              single-line
              hide-details)
            v-spacer
            v-btn(dark).primary
              v-icon(left) add_box
              | ADD TO COHORTS
</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import Header from '@/components/layout/Header.vue';
import DatasetTable from '@/components/DatasetManager/DatasetTable.vue';
import OutcomeTable from '@/components/DatasetManager/OutcomeTable.vue';
import DemographicsTable from '@/components/DatasetManager/DemographicsTable.vue';
import FilterTree from '@/components/DatasetManager/FilterTree.vue';
//  import DonutChart from '@/components/charts/DonutChart.vue';

export default {
  components: {
    datasetTable: DatasetTable,
    // donutChart: DonutChart,
    contentHeader: Header,
    filterTree: FilterTree,
    OutcomeTable,
    DemographicsTable,
  },

  data() {
    return {
      createCohortSheet: false,
      addDataSheet: false,
      search: '',
      outcomes: {
        'UMD': [
          {
            name: 'Motor',
            children: [
              {
                name: 'UPDRS Part I'
              },
              {
                name: 'UDPRS Part II'
              },
              {
                name: 'UPDRS Part III',
              },
              {
                name: 'UPDRS PART IV',
              },
              {
                name: 'UPDRS Total'
              },
            ],
          },
        ],
        'PPMI': [
          {
            name: 'General Disease Severity Measures',
            children: [
              {
                name: 'MDS-UPDRS Part I'
              },
              {
                name: 'MDS-UDPRS Part II'
              },
              {
                name: 'MDS-UPDRS Part III',
              },
              {
                name: 'MDS-UPDRS Part IV',
              },
              {
                name: 'MDS-UPDRS Total'
              },
              {
                name: 'Hoehn and Yahr Stages'
              }
            ],
          },
          {
            name: 'Autonomic',
            children: [
              {
                name: 'SCOPA - Autonomic Dysfunction'
              }
            ]
          },
          {
            name: 'Cognitive',
            children: [
              {
                name: 'Benton Judgment of Line Orientation',
              },
              {
                name: 'Hopkins Verbal Learning Test'
              },
              {
                name: 'Letter Number Sequencing'
              },
              {
                name: 'Montreal Cognitive Assessment',
              },
              {
                name: 'Semantic Fluency'
              },
              {
                name: 'Symbol Digit Modalities',
              },
            ]
          },
          {
            name: 'Sleep',
            children: [
              {
                name: 'Epworth Sleepiness Scale'
              },
              {
                name: 'REM Sleep Behavior Questionnaire'
              }
            ]
          },
          {
            name: 'Mental Health',
            children: [
              {
                name: 'Geriatric Depression Scale'
              },
              {
                name: 'State-Trait Anxiety Inventory'
              }
            ]
          },
          {
            name: 'Disability',
            children: [
              {
                name: 'Modified Schwab & England ADL'
              }
            ]
          },
          {
            name: 'Medical Comorbidities',
            children: [
              {
                name: 'Cumulative Illness Rating Scale'
              }
            ]
          }
]
      }
    };
  },
  filters: {
    buildPath(datasets) {
      // This constructs the build path with selected dataset ids
      if (!datasets) return 'build'

      const idParams = datasets
        .map(dataset => dataset.id)
        .map(id => 'id=' + id)
        .join('&');

      return 'build?' + idParams;
    }
  },
  computed: {
    ...mapState('datasetManager', {
      selectedDatasets: state.SELECTED_DATASETS,
    }),
    buildPathWithParams() {
      if (!this.selectedDatasets) return 'build';
      const idParams = this.selectedDatasets
        .map(dataset => dataset.id)
        .map(id => 'id=' + id)
        .join('&');

      return 'build?' + idParams;
    },
    outcomeMeasures() {
      // Flatten array of outcome measures
      if (!this.selectedDatasets) return [];

      return this.selectedDatasets
        .map(d => d.variables) // get outcome measures
        .reduce((prev, curr) => prev.concat(curr)) // flatten
        .map(v => v.name); // get outcome measure name
    },
  },
  methods: {
    ...mapActions('datasetManager', {
      addSelectedDatasetsToCohorts: actions.ADD_SELECTED_DATASETS_TO_COHORTS,
    }),
  },
};
</script>

<style scoped>
div.v-dialog.v-bottom-sheet.v-bottom-sheet--inset.v-dialog--active {
  overflow: scroll;
}
</style>
