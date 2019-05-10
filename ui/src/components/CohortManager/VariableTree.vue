<template>
  <loading-spinner v-if="isLoading" />
  <v-card v-else>
    <v-card-title card color="white"
      ><span class="title">Variables</span>
    </v-card-title>
    <v-list>
      <draggable
        :list="collection.variables"
        :sortable="false"
        drag-class="v-chip"
        group="variables"
      >
        <v-list-tile
          v-for="variable in collection.variables"
          :key="variable.observation_scale"
        >
          <v-list-tile-content>
            <v-chip> {{ variable.observation_scale }} </v-chip>
          </v-list-tile-content>
        </v-list-tile>
      </draggable>
      <!-- <v-list-group value="true">
        <template v-slot:activator>
          <v-list-tile>
            <v-list-tile-title>Demographics</v-list-tile-title>
          </v-list-tile>
        </template>
        <v-tile-list v-if="!list.length">
          <draggable :list="list" :sortable="false" group="variables" />
        </v-tile-list>
        <v-list-tile v-for="element in list" :key="element.name">
          <v-list-tile-content>
            <draggable :list="list" :sortable="false" group="variables">
              <v-chip>{{ element.name }} </v-chip>
            </draggable>
          </v-list-tile-content>
        </v-list-tile>
      </v-list-group>
      <v-list-group value="true">
        <template v-slot:activator>
          <v-list-tile>
            <v-list-tile-title>Outcome Measures</v-list-tile-title>
          </v-list-tile>
        </template>
        <v-list-group no-action sub-group value="true">
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-title>Motor</v-list-tile-title>
            </v-list-tile>
          </template>

          <v-list-tile v-for="(admin, i) in ['Foo', 'Bar']" :key="i" @click="">
            <v-list-tile-title v-text="admin[0]"></v-list-tile-title>
            <v-list-tile-action>
              <v-icon v-text="admin[1]"></v-icon>
            </v-list-tile-action>
          </v-list-tile>
        </v-list-group>
        <v-list-group sub-group no-action>
          <template v-slot:activator>
            <v-list-tile>
              <v-list-tile-title>Cognitive</v-list-tile-title>
            </v-list-tile>
          </template>
          <v-list-tile v-for="(crud, i) in ['Foo', 'Bar']" :key="i" @click="">
            <v-list-tile-title v-text="crud[0]"></v-list-tile-title>
            <v-list-tile-action>
              <v-icon v-text="crud[1]"></v-icon>
            </v-list-tile-action>
          </v-list-tile>
        </v-list-group>
      </v-list-group> -->
    </v-list>
  </v-card>
</template>

<script>
import draggable from 'vuedraggable';
import { mapState } from 'vuex';
import { state } from '@/store/modules/cohortManager/types';

export default {
  components: {
    draggable,
  },
  data: () => ({
    dragging: false,
  }),
  computed: {
    ...mapState('cohortManager', {
      collection: state.COLLECTION,
      isLoading: state.IS_LOADING,
    }),
  },
  async created() {
    // fetch the shared input and output variables for collection
    // and assign them to variables...
  },
  methods: {
    fetchVariables() {
      // fetch the shared input and output variables for collection
    },
  },
};
</script>

<style lang="scss" scoped></style>
