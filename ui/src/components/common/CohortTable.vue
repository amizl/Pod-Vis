<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
              >{{ title }}
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <!-- no cohorts selected -->
    <v-container
      v-if="!cohorts || cohorts.length == 0"
      fluid
      fill-width
      class="ma-0 pa-0"
    >
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-sheet color="white" class="rounded-lg shadow">
            <div column align-center justify-center fill-width class="py-3">
              <v-subheader class="title primary--text text--lighten-5">
                No cohorts selected.
              </v-subheader>
            </div>
          </v-sheet>
        </v-col>
      </v-row>
    </v-container>

    <!-- cohorts selected -->
    <v-data-table
      v-else
      v-model="selected"
      :headers="headers"
      :items="cohorts"
      item-key="id"
      :show-select="showSelect"
      dense
    >
      <template v-slot:item.label="{ item }">
        <td class="subtitle-1 text-xs-left">{{ item.label }}</td>
      </template>

      <template v-slot:item.size="{ item }">
        <td class="subtitle-1 text-xs-left">{{ item.subject_ids.length }}</td>
      </template>

      <template v-slot:item.query_string="{ item }">
        <td class="subtitle-1 text-xs-left">{{ item.query_string }}</td>
      </template>
    </v-data-table>
  </div>
</template>

<script>
export default {
  props: {
    title: {
      type: String,
      required: false,
      default: 'Cohorts',
    },
    cohorts: {
      type: Array,
      required: true,
    },
    showSelect: {
      type: Boolean,
      required: false,
      default: false,
    },
  },
  data() {
    return {
      selected: [],
      headers: [
        {
          text: 'Cohort Name',
          value: 'label',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Cohort Size',
          value: 'size',
          class: 'text-subtitle-1 font-weight-bold',
        },
        {
          text: 'Query',
          value: 'query_string',
          class: 'text-subtitle-1 font-weight-bold',
        },
      ],
    };
  },
  watch: {
    selected(nsel) {
      this.$emit('selectedCohorts', nsel);
    },
  },
};
</script>

<style></style>
