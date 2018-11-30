<template>
  <v-card class='elevation-3'>
    <v-toolbar
      card
      color="grey lighten-3"
      dense
    >
      <v-icon>settings</v-icon>
      <v-toolbar-title>Filter Datasets</v-toolbar-title>
    </v-toolbar>
    <v-layout>
      <v-flex>
        <v-card-text>
          <v-treeview
            v-model='tree'
            :items='items'
            selectable
          >
          </v-treeview>
        </v-card-text>
      </v-flex>
    </v-layout>
  </v-card>
</template>

<script>
export default {
  data: () => ({
    isLoading: false,
    tree: [],
    items: [
    {
      id: 30,
      name: 'Diseases',
      children: [
        {
          id: 28,
          name: "Parkinson's Disease",
        },
      ]
    },
    {
      id: 2,
      name: 'Outcome Measures',
      children: [
        {
          id: 29,
          name: 'General Disease Severity Measures',
          // children: [
          //   {
          //     id: 3,
          //     name: 'MDS-UPDRS Part I'
          //   },
          //   {
          //     id: 4,
          //     name: 'MDS-UDPRS Part II'
          //   },
          //   {
          //     id: 5,
          //     name: 'MDS-UPDRS Part III',
          //   },
          //   {
          //     id: 6,
          //     name: 'MDS-UPDRS Total'
          //   },
          //     {
          //       id: 31,
          //       name: 'UPDRS Part I',
          //     },
          //     {
          //       id: 32,
          //       name: 'UPDRS Part II',
          //     },
          //     {
          //       id: 33,
          //       name: 'UPDRS Part III',
          //     },
          //     {
          //       id: 34,
          //       name: 'UPDRS Part IV',
          //     },
          //     {
          //       id: 35,
          //       name: 'UPDRS Total',
          //     },
          //     {
          //       id: 36,
          //       name: 'Hoehn and Yahr Stages',
          //     },
          // ],
        },
        {
          id: 7,
          name: 'Autonomic',
          // children: [
          //   {
          //     id: 8,
          //     name: 'SCOPA - Autonomic Dysfunction'
          //   }
          // ]
        },
        {
          id: 9,
          name: 'Cognitive',
          // children: [
          //   {
          //     id: 10,
          //     name: 'Benton Judgment of Line Orientation',
          //   },
          //   {
          //     id: 11,
          //     name: 'Hopkins Verbal Learning Test'
          //   },
          //   {
          //     id: 12,
          //     name: 'Letter Number Sequencing'
          //   },
          //   {
          //     id: 13,
          //     name: 'Montreal Cognitive Assessment',
          //   },
          //   {
          //     id: 14,
          //     name: 'Semantic Fluency'
          //   },
          //   {
          //     id: 15,
          //     name: 'Symbol Digit Modalities',
          //   },
          // ]
        },
        {
          id: 16,
          name: 'Sleep',
          // children: [
          //   {
          //     id: 17,
          //     name: 'Epworth Sleepiness Scale'
          //   },
          //   {
          //     id: 18,
          //     name: 'REM Sleep Behavior Questionnaire'
          //   }
          // ]
        },
        {
          id: 19,
          name: 'Behavior',
          // children: [
          //   {
          //     id: 20,
          //     name: 'Geriatric Depression Scale'
          //   },
          //   {
          //     id: 21,
          //     name: 'State-Trait Anxiety Inventory'
          //   }
          // ]
        },
        {
          id: 22,
          name: 'Disability',
          // children: [
          //   {
          //     id: 23,
          //     name: 'Modified Schwab & England ADL'
          //   },
          //   {
          //     id: 38,
          //     name: 'Older American Resources and Services'
          //   }
          // ]
        },
        {
          id: 36,
          name: 'Medical Comorbidities',
          // children: [
          //   {
          //     id: 37,
          //     name: 'Cumulative Illness Rating Scale'
          //   }
          // ]
        }
      ]
    },
    {
      id: 24,
      name: 'Demographics',
      children: [
        { id: 25, name: 'Age' },
        { id: 26, name: 'Gender' },
        { id: 27, name: 'Race' }
      ]
    },
  ]
  }),
};
</script>

<style scoped>

</style>
