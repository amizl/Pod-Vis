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
      <!-- Add "All:" to select all checkbox -->
      <template v-slot:header.data-table-select="{ on, props }">
        <v-tooltip v-if="!useAutomatedAnalysisMode" top color="primary">
          <template v-slot:activator="{ on: tooltip }">
            <span
              class="text-subtitle-1 font-weight-bold"
              v-on="{ ...tooltip }"
            >
              All: <v-simple-checkbox v-bind="props" v-on="on"
            /></span>
          </template>
          <span>Click to select all variables.</span>
        </v-tooltip>

        <v-tooltip v-else top color="primary">
          <template v-slot:activator="{ on: tooltip }">
            <span
              class="text-subtitle-1 font-weight-bold"
              v-on="{ ...tooltip }"
            >
              Predictors
            </span>
          </template>
          <span
            >Select all variables to use as predictors in the automated
            analysis.</span
          >
        </v-tooltip>
      </template>

      <!-- Header tooltips -->
      <template v-slot:header.output="{ header }">
        <v-tooltip top color="primary">
          <template v-slot:activator="{ on: tooltip }">
            <span
              class="text-subtitle-1 font-weight-bold"
              v-on="{ ...tooltip }"
            >
              Outcomes
            </span>
          </template>
          <span
            >Select all variables to use as outcome variables in the automated
            analysis.</span
          >
        </v-tooltip>
      </template>

      <template
        v-for="(ds, index) in datasets"
        v-slot:[`header.${ds.study_name}`]="{ header }"
      >
        {{ header.dataset.study_name }} <br :key="`dsvc-br-${index}`" />
        <v-chip
          :key="`dsvc-${index}`"
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
          <td v-if="!useAutomatedAnalysisMode">
            <v-checkbox
              :input-value="props.isSelected"
              @change="props.select($event)"
            ></v-checkbox>
          </td>
          <td v-if="useAutomatedAnalysisMode">
            <v-checkbox
              v-model="props.item.isSelectedInput"
              @change="inputCheckboxChange(props, $event)"
            ></v-checkbox>
          </td>
          <td v-if="useAutomatedAnalysisMode">
            <!-- longitudinal outcome variable -->
            <v-select
              v-if="
                isLongitudinal &&
                  props.item.isSelectedInput &&
                  props.item.type == 'observation'
              "
              v-model="props.item.aaWhichOutcome"
              :items="getOutcomeVarVisitChoices(props.item)"
              item-text="name"
              item-value="id"
              label="value to use"
              class="pa-0 ma-0 pt-3"
              dense
            ></v-select>

            <!-- continuous subject variable -->
            <v-select
              v-if="
                props.item.isSelectedInput &&
                  props.item.data_category == 'Continuous' &&
                  props.item.value_type != 'date'
              "
              v-model="props.item.aaRanges"
              :items="['quartiles', 'tertiles', 'halves']"
              label="compare"
              class="pa-0 ma-0 pt-3"
              dense
            ></v-select>
            <!-- categorical subject variable -->
            <v-select
              v-if="
                props.item.isSelectedInput &&
                  (props.item.data_category == 'Categorical' ||
                    props.item.data_category == 'Ordinal')
              "
              v-model="props.item.aaMinCatSize"
              :items="[1, 5, 10, 20, 50]"
              label="minimum category size"
              class="pa-0 ma-0 pt-3"
              dense
            ></v-select>
          </td>
          <td v-if="useAutomatedAnalysisMode">
            <v-checkbox
              v-model="props.item.isSelectedOutput"
              @change="outputCheckboxChange(props, $event)"
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
import { sortScales, estimateMaxSubjects } from '@/utils/helpers';

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
    useAutomatedAnalysisMode: {
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
      colors: colors,
      // auto-analysis
      auto_analysis_inputs: {},
      auto_analysis_inputs_list: [],
      auto_analysis_outputs: {},
      auto_analysis_outputs_list: [],
    };
  },
  computed: {
    isLongitudinal() {
      var is_longitudinal = true;
      this.datasets.forEach(d => {
        if (!d.longitudinal) {
          is_longitudinal = false;
        }
      });
      return is_longitudinal;
    },
    headers() {
      var hdrs = [];
      if (this.useAutomatedAnalysisMode) {
        hdrs.push({
          text: '',
          value: '',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
        });
        hdrs.push({
          text: 'Outcomes',
          value: 'output',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
        });
      }
      hdrs.push({
        text: 'Domain',
        value: 'category',
        sortable: true,
        class: 'text-subtitle-1 font-weight-bold',
      });
      hdrs.push({
        text: 'Variable',
        value: 'scale',
        sortable: true,
        class: 'text-subtitle-1 font-weight-bold',
      });

      // append the dataset study names as headers so
      // we can see study variable distributions as
      // columns
      this.datasets.map(dataset => {
        hdrs.push({
          dataset: dataset,
          text: dataset.study_name,
          value: dataset.study_name,
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
          align: 'center',
        });
      });
      return hdrs;
    },
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
        var ems = estimateMaxSubjects(
          this.subject_variable_visits,
          selectedIds,
          'event'
        );
        this.subject_counts = ems['counts'];
      } else {
        this.subject_counts = this.countSubjects(selectedIds);
      }

      this.$emit('nSubjects', this.subject_counts['all']);
      this.$emit('nSubjectVars', n_subject);
      this.$emit('nObservationVars', n_observation);
    },
    useAutomatedAnalysisMode(aam) {
      if (aam) this.selected = [];
    },
    auto_analysis_inputs_list(ipl) {
      this.$emit('autoAnalysisInputs', ipl);
    },
    auto_analysis_outputs_list(opl) {
      this.$emit('autoAnalysisOutputs', opl);
    },
  },
  async created() {
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
    });

    this.variables = sortScales([...this.variables, ...attributes]);
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
      var nvisits = this.isLongitudinal ? 2 : 1;

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
    inputCheckboxChange(props, evt) {
      var sel = props.item.isSelectedInput;
      if (sel) {
        this.auto_analysis_inputs[props.item.id] = props.item;
        if (
          props.item.data_category == 'Continuous' &&
          props.item.value_type != 'date'
        ) {
          props.item.aaRanges = 'quartiles';
        } else if (
          props.item.data_category == 'Categorical' ||
          props.item.data_category == 'Ordinal'
        ) {
          props.item.aaMinCatSize = 5;
        }
        if (this.isLongitudinal && props.item.type == 'observation') {
          props.item.aaWhichOutcome = 'firstVisit';
        }
        // already selected as output var
        if (props.item.id in this.auto_analysis_outputs) {
          delete props.item.isSelectedOutput;
          delete this.auto_analysis_outputs[props.item.id];
        } else {
          props.select(evt);
        }
      } else {
        delete this.auto_analysis_inputs[props.item.id];
        props.select(evt);
      }
      this.auto_analysis_inputs_list = Object.values(this.auto_analysis_inputs);
      this.auto_analysis_outputs_list = Object.values(
        this.auto_analysis_outputs
      );
    },
    outputCheckboxChange(props, evt) {
      var sel = props.item.isSelectedOutput;
      if (sel) {
        this.auto_analysis_outputs[props.item.id] = props.item;
        // already selected as output var
        if (props.item.id in this.auto_analysis_inputs) {
          delete props.item.isSelectedInput;
          delete this.auto_analysis_inputs[props.item.id];
        } else {
          props.select(evt);
        }
      } else {
        delete this.auto_analysis_outputs[props.item.id];
        if (!(props.item.id in this.auto_analysis_inputs)) props.select(evt);
      }
      this.auto_analysis_inputs_list = Object.values(this.auto_analysis_inputs);
      this.auto_analysis_outputs_list = Object.values(
        this.auto_analysis_outputs
      );
    },
    getOutcomeVarVisitChoices(v) {
      let choices = [
        { id: 'firstVisit', name: 'First Visit' },
        { id: 'lastVisit', name: 'Last Visit' },
      ];
      if (v.data_category == 'Continuous') {
        choices.push({ id: 'change', name: 'Change' });
        choices.push({ id: 'roc', name: 'Rate of Change' });
      }
      return choices;
    },
  },
};
</script>

<style scoped></style>
