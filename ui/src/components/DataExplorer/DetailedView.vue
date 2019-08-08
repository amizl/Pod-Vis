<template>
  <v-sheet color="white" height="100%" class="rounded-lg shadow">
    <v-layout column fill-height class="ma-1">
      <v-card-title class="title primary--text">Detailed View</v-card-title>
      <v-divider></v-divider>
      <v-container fluid fill-height>
        <v-layout column align-center justify-center fill-height>
          <v-subheader
            v-if="!detailedView"
            class="display-1 primary--text text--lighten-5"
          >
            SELECT OUTCOME VARIABLE
          </v-subheader>
          <loading-spinner v-else></loading-spinner>
        </v-layout>
      </v-container>
    </v-layout>
  </v-sheet>
</template>

<script>
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataExplorer/types';

export default {
  computed: {
    ...mapState('dataExplorer', {
      detailedView: state.DETAILED_VIEW,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
