<template>
  <transition name="fade" mode="out-in">
    <loading-spinner v-if="isLoading" medium class="pb-5" />
    <v-data-table
      v-else
      v-model="selected"
      class="ml-1 mr-1"
      :items="variables"
      item-key="scale"
      :headers="headers"
      disable-pagination
      hide-default-footer
      show-select
    >
      <template
        v-for="ds in datasets"
        v-slot:[`header.${ds.study_name}`]="{ header }"
      >
          {{ header.dataset.study_name }} <br />
          <v-chip
            :color="getNumSubjectsColor(getStudyCount(header.dataset.id))"
            :text-color="
              getNumSubjectsTextColor(getStudyCount(header.dataset.id))
            "
            class="title ma-2"
            >{{ getStudyCount(header.dataset.id) + ' selected' }}</v-chip
          >
      </template>

      <!--
      <template v-slot:header.="{ header }">
        <tr>
	  <th></th>
          <th class="text-subtitle-1 text-xs-left">Domain<br /></th>
          <th class="text-subtitle-1 text-xs-left">Variable<br /></th>
          <th
            v-for="dataset in datasets"
            :key="dataset.id"
            class="text-subtitle-1 text-xs-center"
          >
            {{ dataset.study_name }}<br />
            <v-chip
              disabled
              :color="getNumSubjectsColor(getStudyCount(dataset.id))"
              :text-color="getNumSubjectsTextColor(getStudyCount(dataset.id))"
              class="title ma-2"
              >{{ getStudyCount(dataset.id) + ' selected' }}</v-chip
            >
          </th>
        </tr>
      </template>
      -->

      <template v-slot:item="props">
        <tr>
          <td>
            <v-checkbox
              :input-value="props.isSelected"
              @change="props.select($event)"
            ></v-checkbox>
          </td>
          <td class="subtitle-1 text-xs-left">
	      <v-row align="center" class="pa-0 ma-0">
              <span style="padding:0.5em 0.5em 0em 0em"
                ><img
                  :src="'/images/' + props.item.category + '-icon-128.png'"
                  :title="props.item.category"
                  style="height:2.5em"
              /></span>
              {{ props.item.category }}
	      </v-row>
          </td>
          <td class="subtitle-1 text-xs-left">
            <span>{{ props.item.scale }}</span>
          </td>

          <td
            v-for="dataset in datasets"
            :key="dataset.id"
            class="subtitle-1 text-xs-center"
            >
	    <v-container class="pa-0 ma-0">
	    <v-row justify="center" class="pa-0 ma-0">
            <histogram-sparkline
              :dataset-id="dataset.id"
              :type="props.item.type"
              :scale-id="props.item.id"
              :data-category="props.item.data_category"
              />
	    </v-row>
	    <v-row justify="center" class="pa-0 ma-0">
            <span
              :style="
                'color: ' +
                  getStudyVariableColor(
                    getStudyVariableCount(dataset.id, props.item.id)
                  )
              "
            >
              {{ getStudyVariableCount(dataset.id, props.item.id) }}</span
								      >
	    </v-row></v-container>
          </td>
        </tr>
      </template>
    </v-data-table>
  </transition>
</template>

<script>
import axios from 'axios';
import HistogramSparkline from '@/components/DatasetManager/HistogramSparkline.vue';
import {
  colors,
  getNumSubjectsColor,
  getNumSubjectsTextColor,
} from '@/utils/colors';

export default {
  components: {
    HistogramSparkline,
  },
  props: {
    value: {
      type: [Array, null],
      default: () => [],
    },
    datasets: {
      type: Array,
      default: () => [],
    },
    selectable: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: true,
      selected: [],
      variables: [],
      subject_variables: {},
      study_variable_counts: {},
      subject_counts: { all: 0 },
      headers: [
        {
          text: 'Category',
          value: 'category',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Scale',
          value: 'scale',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
      colors: colors,
    };
  },
  watch: {
    /**
     * When the table updates the selected array,
     * we want to notify our parent by emitting the
     * input event. That way its v-model and keep
     * its prop in sync.
     */
    selected(value) {
      if (this.selectable) this.$emit('input', value);

      // track number of selected subject and observation_variables
      var n_subject = 0;
      var n_observation = 0;

      value.forEach(v => {
        if (v.type === 'subject') {
          n_subject += 1;
        } else if (v.type === 'observation') {
          n_observation += 1;
        }
      });

      var selectedIds = value.map(v => v['id']);
      this.subject_counts = this.countSubjects(selectedIds);
      this.$emit('nSubjects', this.subject_counts['all']);
      this.$emit('nSubjectVars', n_subject);
      this.$emit('nObservationVars', n_observation);
    },
  },
  async created() {
    this.headers = [
      ...this.headers,
      // append the dataset study names as headers so
      // we can see study variable distributions as
      // columns
      ...this.datasets.map(dataset => ({
        dataset: dataset,
        text: dataset.study_name,
        value: dataset.study_name,
        sortable: false,
        class: 'text-subtitle-1 font-weight-bold',
        align: 'center'
      })),
    ];

    const {
      data: { variables },
    } = await this.fetchSharedVariables();
    // add type key to variables to distinguish that these variables
    // are relating to the observations
    variables.forEach(variable => {
      variable.type = 'observation';
    });
    variables.forEach(x => {
      x.full_path = x.category + '/' + x.scale;
    });
    this.variables = variables;

    const { data: subjVars } = await this.fetchSubjectVariables();
    this.subject_variables = subjVars['subjects'];

    // build hash that maps variable_id + study_id -> number of subjects
    this.computeStudyVariableCounts();

    // fetch shared subject attributes
    const {
      data: { attributes },
    } = await this.fetchSharedAttributes();

    // add type key to subject variables to distinguish that these variables
    // are relating to the subjects
    attributes.forEach(variable => {
      variable.type = 'subject';
      variable.full_path = variable.category + '/' + variable.scale;
      // TODO - retrieve data_category from database
      variable.data_category = 'Unknown';
    });
    this.variables = [...this.variables, ...attributes];
    this.isLoading = false;
  },
  methods: {
    getNumSubjectsColor,
    getNumSubjectsTextColor,
    /**
     * If dataset id is an array of ids, we want to
     * call the API endpoint that gets their intersecting
     * variables.
     */
    fetchSharedVariables() {
      const base = `/api/studies/variables`;
      const query = this.datasets.map(({ id }) => `id=${id}`).join('&');
      return axios.get(`${base}?${query}`);
    },
    fetchSharedAttributes() {
      const base = `/api/studies/attributes`;
      const query = this.datasets.map(({ id }) => `id=${id}`).join('&');
      return axios.get(`${base}?${query}`);
    },
    /**
     * Retrieve list of subjects along with the variables measured (first + last) for each.
     */
    fetchSubjectVariables() {
      const base = `/api/studies/subject_variables`;
      const query = this.datasets.map(({ id }) => `id=${id}`).join('&');
      return axios.get(`${base}?${query}`);
    },
    /**
     * Build hash that maps variable_id + study_id -> number of subjects
     */
    computeStudyVariableCounts() {
      var svc = {};
      const subj_ids = Object.keys(this.subject_variables);
      subj_ids.forEach(subj_id => {
        var study_ids = Object.keys(this.subject_variables[subj_id]);
        study_ids.forEach(study_id => {
          var var_ids = Object.keys(this.subject_variables[subj_id][study_id]);
          var_ids.forEach(var_id => {
            var key = var_id + ':' + study_id;
            if (!(key in svc)) {
              svc[key] = 0;
            }
            svc[key] = svc[key] + 1;
          });
        });
      });
      this.study_variable_counts = svc;
    },

    getStudyVariableCount(study_id, var_id) {
      var key = var_id + ':' + study_id;
      var count = 0;
      if (key in this.study_variable_counts) {
        count = this.study_variable_counts[key];
      }
      return count;
    },

    getStudyVariableColor(nSubjects) {
      if (nSubjects <= 25) {
        return '#F83008';
      } else {
        return 'black';
      }
    },

    getStudyCount(study_id) {
      if (study_id in this.subject_counts) {
        return this.subject_counts[study_id];
      } else {
        return 0;
      }
    },

    /**
     * Count the number of subjects in the Dataset for a given list of variable ids.
     */
    countSubjects(var_ids) {
      var nSubjects = { all: 0 };

      if (var_ids.length === 0) return nSubjects;
      this.datasets.forEach(d => {
        nSubjects[d.id] = 0;
      });

      const subj_ids = Object.keys(this.subject_variables);
      subj_ids.forEach(subj_id => {
        var include_subject = true;
        var study_ids = Object.keys(this.subject_variables[subj_id]);
        study_ids.forEach(study_id => {
          const svars = this.subject_variables[subj_id][study_id];
          // check for presence of all requested vars:
          var_ids.forEach(v => {
            if (!(v in svars)) {
              include_subject = false;
            }
          });
          if (include_subject) {
            nSubjects[study_id] += 1;
            nSubjects['all'] += 1;
          }
        });
      });
      return nSubjects;
    },
  },
};
</script>

<style scoped></style>
