<template>
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
        <!-- <td v-if="histogram"></td> -->
        <!-- <td>{{ props.item.description }}</td> -->
        <!-- <td>{{ props.item.data_range }}</td> -->
        <!-- <td>{{ props.item.missing }}</td> -->
      </tr>
    </template>
    <template v-slot:no-data>
      <v-alert :value="true" color="info" icon="info">
        No missing variables.
      </v-alert>
    </template>
  </v-data-table>
</template>

<script>
import axios from 'axios';

export default {
  props: {
    value: {
      type: [Array, null],
      default: () => [],
    },
    selectedIds: {
      type: [Array],
      default: () => [],
    },
    datasetId: {
      type: [Number, Array],
      default: 0,
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
    let {
      data: { variables: sharedVariables },
    } = await this.fetchSharedVariables();
    let {
      data: { variables },
    } = await this.fetchVariables();

    const missingVariables = variables
      .map(variable => variable.scale)
      .filter(
        scale =>
          !sharedVariables.map(variable => variable.scale).includes(scale)
      );

    this.variables = missingVariables;
    this.variables.forEach(v => (v['type'] = 'observation'));

    // TODO: Check subject variables are missing from shared subject variables
    // const {
    //   data: { subject_attributes: attrs },
    // } = await axios.get(`/api/studies/${this.datasetId}/subjects/attributes`);

    // attrs.forEach(a => (a['type'] = 'subject'));
    // this.variables = [...this.variables, ...attrs];
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
      const query = this.selectedIds.map(id => `id=${id}`).join('&');
      return axios.get(`${base}?${query}`);
    },
    /**
     * API endpoint for getting a dataset's variables.
     */
    fetchVariables() {
      return axios.get(`/api/studies/${this.datasetId}/variables`);
    },
  },
};
</script>

<style scoped></style>
