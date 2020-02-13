<template>
  <transition name="fade" mode="out-in">
    <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
    <v-data-table
      v-else
      v-model="selected"
      :headers="headers"
      :items="variables"
      :select-all="selectable"
      item-key="scale"
      :pagination.sync="pagination"
      class="ml-1 mr-1"
      hide-actions
    >
      <template v-slot:items="props">
        <tr>
          <td v-if="selectable">
            <v-checkbox v-model="props.selected" color="primary" hide-details />
          </td>
          <td>
            <v-layout align-center
              ><span style="padding:0.5em 0.5em 0.25em 0em"
                ><img
                  :src="'/images/' + props.item.category + '-icon-128.png'"
                  :title="props.item.category"
                  style="height:3.5em"
              /></span>
              {{ props.item.category }}</v-layout
            >
          </td>
          <td>{{ props.item.scale }}</td>
        </tr>
      </template>
      <template v-slot:no-data>
        <v-alert :value="true" color="primary" icon="info">
          No missing variables.
        </v-alert>
      </template>
    </v-data-table>
  </transition>
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
      pagination: { sortBy: 'full_path', rowsPerPage: -1 },
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
    const {
      data: { variables: sharedVariables },
    } = await this.fetchSharedVariables();
    const {
      data: { variables },
    } = await this.fetchVariables();

    const missingVariables = variables
      .map(variable => variable.scale)
      .filter(
        scale =>
          !sharedVariables.map(variable => variable.scale).includes(scale)
      );

    missingVariables.forEach(v => {
      v.type = 'observation';
      v.full_path = v.category + '/' + v.scale;
    });
    this.variables = missingVariables;

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
