<template>
  <layout>
    <!-- <v-chip
      v-for="variable in inputVariables"
      :key="variable.label"
      class="handle"
      :color="
        variable.type == 'subject' ? 'primary lighten-3' : 'primary lighten-3'
      "
    >
      {{ variable.label }}
    </v-chip> -->
  </layout>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';

export default {
  computed: {
    ...mapState('cohortManager', {
      inputVariables: state.INPUT_VARIABLES,
    }),
  },
};
</script>

<style scoped></style>
