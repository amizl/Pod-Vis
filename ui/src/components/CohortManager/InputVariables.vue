<template>
  <v-card>
    <v-card-title card color="white">
      <span class="title">Input Variables:</span>
      <draggable :list="variables" group="variables">
        <v-chip v-for="variable in variables" :key="variable.id">{{
          variable.observation_scale
        }}</v-chip>
      </draggable>
    </v-card-title>
  </v-card>
</template>

<script>
import draggable from 'vuedraggable';

export default {
  components: {
    draggable,
  },
  data() {
    return {
      variables: [],
    };
  },
};
</script>

<style lang="scss" scoped></style>
