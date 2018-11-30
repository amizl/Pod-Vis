<template>
  <v-container
    fluid
    grid-list-lg
    v-if='dataset'
  >
    <v-toolbar
      app
      class="primary"
    >
      <v-toolbar-items>
        <v-btn
          flat
          dark
          @click='goBack'
        >
          <v-icon left>
            arrow_back
          </v-icon>
          BACK TO DATASET MANAGER
        </v-btn>
      </v-toolbar-items>
    </v-toolbar>
    <v-layout
      row
      wrap
      justify-center
    >
      <v-flex xs4>
        <v-card>
          <v-toolbar card dense>
            <v-toolbar-title>
              DATASET DESCRIPTION
            </v-toolbar-title>
          </v-toolbar>
          <div class='ma-2'>
            <v-card-title
              primary-title
            >
              <h3>
                {{ dataset.dataset }}
              </h3>
            </v-card-title>
            <v-card-text
            >
              <p>{{ dataset.description }}</p>
            </v-card-text>
          </div>
        </v-card>
      </v-flex>
      <v-flex xs4>
        <v-card>
          <v-toolbar card dense>
            <v-toolbar-title>
              SUBJECT SUMMARY
            </v-toolbar-title>
          </v-toolbar>
          <v-card-title></v-card-title>
        </v-card>
      </v-flex>
      <v-flex xs8>
        <v-card>
          <v-toolbar card dense>
            <v-toolbar-title>
              VARIABLES
            </v-toolbar-title>
          </v-toolbar>
          <variable-table v-if='dataset' :variables='dataset.variables'></variable-table>
        </v-card>
      </v-flex>
    </v-layout>
  </v-container>

</template>

<script>
import { mapState, mapActions } from 'vuex';
import { state, actions } from '@/store/modules/datasetManager/types';
import * as firebase from 'firebase';
import VariableTable from '@/components/DatasetManager/VariableTable.vue';

export default {
  props: {
    id: String,
  },
  components: {
    VariableTable,
  },
  data() {
    return {
      dataset: null,
    }
  },
  computed: {
    ...mapState('datasetManager', {
      loading: state.IS_LOADING,
      datasets: state.DATASETS
    }),
  },
  async created() {
    const dataset = await this.fetchDataset(this.id);
    if (dataset.exists) {
      this.dataset = dataset.data();
    }
  },
  methods: {
    goBack() {
      this.$router.go(-1);
    },
    fetchDataset() {
      return firebase
        .firestore()
        .collection('datasets')
        .doc(this.id)
        .get()
    }
  }
}
</script>

<style scoped>
</style>
