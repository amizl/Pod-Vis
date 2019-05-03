<template>
  <transition name="fade" mode="out-in">
    <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
    <v-data-table
      v-else
      :headers="headers"
      :items="variables"
      v-model="selected"
      :select-all="selectable"
      item-key="scale"
      must-sort
    >
      <template v-slot:items="props">
        <tr>
          <td v-if="selectable">
            <v-checkbox v-model="props.selected" color="primary" hide-details />
          </td>
          <td>{{ props.item.category }}</td>
          <td>{{ props.item.scale }}</td>
          <td
            v-for="dataset in datasets"
            :key="dataset.id"
            class="text-xs-center"
          >
            <histogram-sparkline
              :dataset-id="dataset.id"
              :type="props.item.type"
              :scale="props.item.scale"
            />
          </td>
        </tr>
      </template>
    </v-data-table>
  </transition>
</template>

<script>
import axios from 'axios';
import VariableSparkline from '@/components/DatasetManager/VariableSparkline.vue';
import HistogramSparkline from '@/components/DatasetManager/HistogramSparkline.vue';

export default {
  components: {
    VariableSparkline,
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
      headers: [
        {
          text: 'Category',
          value: 'category',
          sortable: true,
        },
        {
          text: 'Scale',
          value: 'scale',
          sortable: true,
        },
        // {
        //   text: 'Variable',
        //   value: 'variable',
        // },
        // {
        //   text: 'Type',
        //   value: 'type',
        // },
        // {
        //   text: 'Description',
        //   value: 'description',
        // },
        // {
        //   text: 'Data Range',
        //   value: 'data_range',
        // },
        // {
        //   text: 'Missing',
        //   value: 'missing',
        // },
        // {
        //   text: 'Histogram',
        //   value: 'histogram',
        // },
      ],
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
    },
  },
  async created() {
    this.headers = [
      ...this.headers,
      // append the dataset study names as headers so
      // we can see study variable distributions as
      // columns
      ...this.datasets.map(dataset => ({
        text: dataset.study_name,
        value: dataset.study_name,
        sortable: false,
      })),
    ];

    const {
      data: { variables },
    } = await this.fetchSharedVariables();
    // add type key to variables to distinguish that these variables
    // are relating to the observations
    variables.forEach(variable => (variable['type'] = 'observation'));
    this.variables = variables;

    const {
      data: { subject_attributes: subjectVariables },
    } = await axios.get(
      `/api/studies/${this.datasets[0].id}/subjects/attributes`
    );
    // add type key to subject variables to distinguish that these variables
    // are relating to the subejcts
    subjectVariables.forEach(variable => (variable['type'] = 'subject'));
    this.variables = [...this.variables, ...subjectVariables];

    this.isLoading = false;
  },
  methods: {
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
  },
};
</script>

<style scoped></style>
