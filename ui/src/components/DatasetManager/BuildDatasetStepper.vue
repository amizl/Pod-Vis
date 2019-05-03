<template>
  <v-card class="elevation-5">
    <v-card-text>
      <v-stepper v-model="currentStep" class="elevation-0">
        <v-stepper-header class="elevation-0">
          <template v-for="({ step, title }, index) in steps">
            <v-stepper-step
              :key="index"
              :step="step"
              :complete="currentStep > step"
            >
              {{ title }}
            </v-stepper-step>
            <v-divider v-if="step !== steps.length" :key="index"></v-divider>
          </template>
        </v-stepper-header>
        <v-stepper-items>
          <v-stepper-content
            v-for="({ step, component, data }, index) in steps"
            :key="index"
            :step="step"
          >
            <v-card>
              <v-card-text>
                <component :is="component" :data="data"></component>
              </v-card-text>
            </v-card>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </v-card-text>
    <v-card-actions>
      <v-spacer></v-spacer>
      <v-btn v-if="!isAtBeginning" flat @click="currentStep--">
        Previous
        <!-- {{ lastStep }} -->
      </v-btn>
      <v-btn v-if="!isAtEnd" color="primary" @click="currentStep++">
        Next
        <!-- {{ nextStep }} -->
      </v-btn>
    </v-card-actions>
  </v-card>
</template>

<script>
// import FilterTree from '@/components/DatasetManager/FilterTree.vue';
import HierarchicalHeatmap from '@/components/charts/HierarchicalHeatmap.vue';

export default {
  props: {
    outcomeMeasures: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      currentStep: 1,
      steps: [
        {
          step: 1,
          title: 'Compare Outcome Measures',
          component: HierarchicalHeatmap,
          data: this.outcomeMeasures,
        },
        {
          step: 2,
          title: 'Compare Variables',
          component: 'div',
        },
        {
          step: 3,
          title: 'Transform',
          component: 'div',
        },
        {
          step: 4,
          title: 'Save to Dashboard',
          component: 'div',
        },
      ],
    };
  },
  computed: {
    isAtBeginning() {
      // Used to destroy previous button when at start
      return this.currentStep === 1;
    },
    isAtEnd() {
      // Used to destory next button when at the end
      return this.currentStep === this.steps.length;
    },
    nextStep() {
      // Return the title of the next step
      const { title } = this.steps.find(
        ({ step }) => step === this.currentStep + 1
      );
      return title;
    },
    lastStep() {
      // Return title of previous step
      const { title } = this.steps.find(
        ({ step }) => step === this.currentStep - 1
      );

      return title;
    },
  },
};
</script>

<style scoped></style>
