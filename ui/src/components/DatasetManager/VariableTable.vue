<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    v-model="selected"
    :headers="headers"
    :items="variables"
    :select-all="selectable"
    item-key="scale"
    must-sort
    hide-actions
    class="pb-1"
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
    datasetId: {
      type: [Number, Array],
      default: 0,
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
    const { data } =
      this.datasetId instanceof Array
        ? await this.fetchSharedVariables()
        : await this.fetchVariables();
    this.variables = data.variables;
    this.variables.forEach(v => (v['type'] = 'observation'));

    const res = await axios.get(
      `/api/studies/${this.datasetId}/subjects/attributes`
    );
    const attrs = res.data.subject_attributes;
    attrs.forEach(a => (a['type'] = 'subject'));
    this.variables = [...this.variables, ...res.data.subject_attributes];
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
      const query = this.datasetId.map(id => `id=${id}`).join('&');
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
