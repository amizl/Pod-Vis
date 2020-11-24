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
      <!-- Attempt to add 'Select All:' label to master checkbox. -->
      <!--
      <template v-slot:header.data-table-select="{ header }">
        <span class="text-subtitle-1 font-weight-bold">Select All:</span>
      </template>
      -->
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
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <span v-on="{ ...tooltip }">
                  {{
                    useLongScaleNames
                      ? props.item.scale
                      : props.item.abbreviation
                  }}
                </span>
              </template>
              <span
                v-html="
                  useLongScaleNames ? props.item.description : props.item.scale
                "
              ></span>
            </v-tooltip>
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
              </v-row></v-container
            >
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
import { sortScales } from '@/utils/helpers';

export default {
  components: {
    HistogramSparkline,
  },
  props: {
    datasets: {
      type: Array,
      default: () => [],
    },
    selectable: {
      type: Boolean,
      default: false,
    },
    useMoreAccurateSubjectCounts: {
      type: Boolean,
      default: false,
    },
    useLongScaleNames: {
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
      subject_variable_visits: {},
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

      var selectedIds = value.map(v => v.id);
      if (this.useMoreAccurateSubjectCounts) {
        // TODO - check visit_num also and return the higher of the two
        this.subject_counts = this.estimateMaxSubjects(selectedIds, 'event');
      } else {
        this.subject_counts = this.countSubjects(selectedIds);
      }

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
        align: 'center',
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

    if (this.useMoreAccurateSubjectCounts) {
      const { data: subjVarVisits } = await this.fetchSubjectVariableVisits();
      this.subject_variable_visits = subjVarVisits['visits'];
    } else {
      const { data: subjVars } = await this.fetchSubjectVariables();
      this.subject_variables = subjVars['subjects'];
    }

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

    this.variables = sortScales([...this.variables, ...attributes]);
    this.isLoading = false;
  },
  methods: {
    getNumSubjectsColor,
    getNumSubjectsTextColor,
    isLongitudinal() {
      var is_longitudinal = true;
      this.datasets.forEach(d => {
        if (!d.i_longitudinal) {
          is_longitudinal = false;
        }
      });
      return is_longitudinal;
    },
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
     * Retrieve list of subjects along with the variables measured at each visit.
     */
    fetchSubjectVariableVisits() {
      const base = `/api/studies/subject_variable_visits`;
      const query = this.datasets.map(({ id }) => `id=${id}`).join('&');
      return axios.get(`${base}?${query}`);
    },
    /**
     * Build hash that maps variable_id + study_id -> number of subjects
     */
    computeStudyVariableCounts() {
      var svc = {};
      var svars = this.useMoreAccurateSubjectCounts
        ? this.subject_variable_visits['subjects']
        : this.subject_variables;
      var nvisits = this.isLongitudinal() ? 2 : 1;

      const subj_ids = Object.keys(svars);
      subj_ids.forEach(subj_id => {
        var study_ids = Object.keys(svars[subj_id]);
        study_ids.forEach(study_id => {
          var var_ids = Object.keys(svars[subj_id][study_id]);
          var_ids.forEach(var_id => {
            var key = var_id + ':' + study_id;
            var add_one = true;

            // check for the expected number of measurements
            if (this.useMoreAccurateSubjectCounts) {
              if (typeof svars[subj_id][study_id][var_id] != 'number') {
                var evtStr = svars[subj_id][study_id][var_id]['event'];
                var nEvt = evtStr.split('1').length - 1;
                var numStr = svars[subj_id][study_id][var_id]['num'];
                var nNum = numStr.split('1').length - 1;
                if (nEvt < nvisits && nNum < nvisits) add_one = false;
              }
            }

            if (add_one) {
              if (!(key in svc)) {
                svc[key] = 0;
              }
              svc[key] = svc[key] + 1;
            }
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

    /**
     * Given a list of [variable_id, first_index, last_index], generate a set of subject counts
     * using the data in subject_variable_visits.
     *
     * which - either 'event' or 'num'
     */
    countSubjectsByVisits(vars, which) {
      var subjCounts = { all: 0 };
      var studyVarCounts = {};
      var subjs = this.subject_variable_visits['subjects'];
      var subjIds = Object.keys(subjs);

      subjIds.forEach(sid => {
        var s = subjs[sid];
        var include_subj = true;
        var study_ids = Object.keys(s);
        study_ids.forEach(study_id => {
          if (!(study_id in subjCounts)) {
            subjCounts[study_id] = 0;
          }
          vars.forEach(v => {
            if (!(v[0] in s[study_id])) {
              include_subj = false;
            } else if (typeof s[study_id][v[0]] != 'number') {
              var vstring = s[study_id][v[0]][which];
              if (vstring.charAt(v[1]) == '0' || vstring.charAt(v[2]) == '0') {
                include_subj = false;
              }
            }
          });
        });
        if (vars.length > 0 && include_subj) {
          subjCounts['all'] += 1;
          study_ids.forEach(study_id => {
            subjCounts[study_id] += 1;
          });
        }
      });
      return subjCounts;
    },

    /**
     * Determine the maximum number of subjects that could be obtained with the selected
     * set of variables, assuming optimal first/last visit selection.
     *
     * which - either 'event' or 'num'
     */
    estimateMaxSubjects(var_ids, which) {
      var subjs = this.subject_variable_visits['subjects'];
      var subjIds = Object.keys(subjs);
      var visits = this.subject_variable_visits['visits'][which];
      var n_visits = visits.length;

      // simple heuristic based on selecting the two visits from each variable with the most subjects
      var vars = [];

      var_ids.forEach(vid => {
        // get visit counts for variable vid
        var visitCounts = [];

        subjIds.forEach(sid => {
          var s = subjs[sid];
          var study_ids = Object.keys(s);
          study_ids.forEach(study_id => {
            if (vid in s[study_id] && typeof s[study_id][vid] != 'number') {
              var vstring = s[study_id][vid][which];
              for (var vis = 0; vis < n_visits; ++vis) {
                if (!(vis in visitCounts))
                  visitCounts[vis] = { index: vis, count: 0 };
                if (vstring.charAt(vis) == '1') {
                  visitCounts[vis]['count'] += 1;
                }
              }
            }
          });
        });

        // heuristic - sort by size and pick the top two, then sort by index
        visitCounts.sort((a, b) => b['count'] - a['count']);
        var first_index = 0;
        var last_index = 0;

        if (visitCounts.length > 1) {
          if (visitCounts[0]['index'] < visitCounts[1]['index']) {
            first_index = visitCounts[0]['index'];
            last_index = visitCounts[1]['index'];
          } else {
            first_index = visitCounts[1]['index'];
            last_index = visitCounts[0]['index'];
          }
        }
        vars.push([vid, first_index, last_index]);
      });
      var counts = this.countSubjectsByVisits(vars, which);
      return counts;
    },
  },
};
</script>

<style scoped></style>
