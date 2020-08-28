<template>
  <v-data-table
    :headers="headers"
    :items="variables"
    item-key="scale"
    dense
    must-sort
    hide-default-footer
    disable-pagination
    class="pb-1"
  >
    <template v-slot:item.category_icon="{ item }">
      <td class="subtitle-1 text-xs-left">
        <v-row align="center" class="pl-2"
          ><img
            :src="'/images/' + item.ontology.category + '-icon-128.png'"
            :title="item.ontology.category"
            style="height:2.5em"
            class="pa-1"
          />
        </v-row>
      </td>
    </template>

    <template v-slot:item.category="{ item }">
      <td class="subtitle-1 text-xs-left">
        <v-row align="center" class="pl-2"> {{ item.ontology.category }}</v-row>
      </td>
    </template>

    <template v-slot:item.scale="{ item }">
      <td class="subtitle-1 text-xs-left">
        <v-tooltip top color="primary">
          <template v-slot:activator="{ on: tooltip }">
            <span v-on="{ ...tooltip }">
              {{ item.ontology.abbreviation }}
            </span>
          </template>
          <span>{{ item.ontology.label }}</span>
        </v-tooltip>
      </td>
    </template>

    <template v-slot:item.data_category="{ item }">
      <td class="subtitle-1 text-xs-left">{{ item.ontology.data_category }}</td>
    </template>

    <template v-slot:item.first_visit="{ item }">
      <td class="subtitle-1 text-xs-left">{{ getFirstVisit(item) }}</td>
    </template>

    <template v-slot:item.last_visit="{ item }">
      <td class="subtitle-1 text-xs-left">{{ getLastVisit(item) }}</td>
    </template>

    <template v-slot:item.flip_axis="{ item }">
      <td class="subtitle-1 text-xs-left">{{ getFlipAxis(item) }}</td>
    </template>
  </v-data-table>
</template>

<script>
export default {
  props: {
    variables: {
      type: [Array, null],
      default: () => [],
    },
    dense: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      headers: [
        {
          text: '',
          value: 'category_icon',
          sortable: false,
          class: 'text-subtitle-1 font-weight-bold',
        },
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
        {
          text: 'Data Category',
          value: 'data_category',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'First Visit',
          value: 'first_visit',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Last Visit',
          value: 'last_visit',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Flip Axis?',
          value: 'flip_axis',
          sortable: true,
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
    };
  },
  methods: {
    getFirstVisit(item) {
      if (item.first_visit_event != null) {
        return item.first_visit_event;
      } else if (item.first_visit_num != null) {
        return item.first_visit_num;
      }
      return '';
    },
    getLastVisit(item) {
      if (item.last_visit_event != null) {
        return item.last_visit_event;
      } else if (item.last_visit_num != null) {
        return item.last_visit_num;
      }
      return '';
    },
    getFlipAxis(item) {
      if (item.ontology.data_category == 'Categorical') {
        return '-';
      }
      return item.ontology.flip_axis ? 'Yes' : 'No';
    },
  },
};
</script>

<style scoped></style>
