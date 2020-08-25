<template>
  <loading-spinner v-if="isLoading" medium class="pb-5"></loading-spinner>
  <v-data-table
    v-else
    v-model="selected"
    :headers="headers"
    :items="variables"
    item-key="scale"
    must-sort
    hide-default-footer
    disable-pagination
    class="pb-1"
  >
    <template v-slot:item.category="{ item }">
      <td class="subtitle-1 text-xs-left nowrap">
	<v-row fill-height align="center" class="nowrap">
	<img
              :src="'/images/' + item.category + '-icon-128.png'"
              :title="item.category"
              style="height:2.5em;"
          /><span class="pl-2" height="100%">{{ item.category }}</span></v-row>
      </td>
    </template>

    <template v-slot:item.abbreviation="{ item }">
      <td class="subtitle-1 text-xs-left nowrap">
        <v-tooltip top color="primary">
          <template v-slot:activator="{ on: tooltip }">
            <span v-on="{ ...tooltip }"> {{ item.abbreviation }} </span>
          </template>
          <span>{{ item.scale }}</span>
        </v-tooltip>
      </td>
    </template>

    <template v-slot:item.description="{ item }">
      <td class="subtitle-1 text-xs-left">
        <span class="subtitle-2">{{ item.scale }}: </span>
        <span v-html="item.description"></span>
      </td>
    </template>
  </v-data-table>
</template>

<script>
import axios from 'axios';
import { sortScales } from '@/utils/helpers';

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
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Scale',
          value: 'abbreviation',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Description',
          value: 'description',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold descr',
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
    const { data } =
      this.datasetId instanceof Array
        ? await this.fetchSharedVariables()
        : await this.fetchVariables();
    this.variables = data.variables;
    this.variables.forEach(v => {
      v.type = 'observation';
    });

    const res = await axios.get(
      `/api/studies/${this.datasetId}/subjects/attributes`
    );
    const attrs = res.data.subject_attributes;
    attrs.forEach(a => {
      a.type = 'subject';
    });
    this.variables = sortScales([...this.variables, ...res.data.subject_attributes]);
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

<style scoped>
td.nowrap { word-break: keep-all; white-space: nowrap; }
</style>
