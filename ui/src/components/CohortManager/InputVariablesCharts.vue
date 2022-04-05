<template>
  <div class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
        <v-card
      
        v-for="(inputVariable, index) in reorderVariables(newTitle, [
          ...inputVariables
        ])"
        :key="'ivcc-' + inputVariable.id"
        :class="index > 0 ? 'ml-2 pb-1' : 'pb-1'"
      >
        <input-variable-chart
          :ref="'ivc-' + inputVariable.id"
          :key="'ivc-' + inputVariable.id"
          :variable="inputVariable"
          :show-filter-help="showFilterHelp"
          :show-analytics-help="showAnalyticsHelp"
          @userResetInputVariable="userChangedVariable"
          @userChangedInputVariable="userChangedVariable"
          @comparePredefinedRanges="comparePredefinedRanges"
          @savePredefinedRanges="savePredefinedRanges"
        />
      </v-card>
    </v-card>
  </div>
</template>

<script>
import { mapState } from "vuex";
import { state } from "@/store/modules/cohortManager/types";
import InputVariableChart from "@/components/CohortManager/InputVariableChart.vue";
import resize from "vue-resize-directive";

export default {
    data: () => ({
    //orderedInputVariables: this.$store.state.INPUT_VARIABLES,
    items: [
      { title: "Alphabetical" },
      { title: "Variable" },
      { title: "Selection" },
      { title: "Domain" }
    ],
    // sort: false,
    newTitle: null
  }),
  directives: {
    resize
  },
  components: {
    InputVariableChart
  },
  props: {
    showFilterHelp: {
      type: Boolean,
      required: false,
      default: false
    },
    showAnalyticsHelp: {
      type: Boolean,
      required: false,
      default: false
    }
  },
  computed: {
    ...mapState("cohortManager", {
      inputVariables: state.INPUT_VARIABLES,
      sort: state.SORT
    })
  },
  methods: {
    reorderVariables: function(title, inputVariables) {
      console.log(
        this.sort +
          " test " +
          title +
          " " +
          [...inputVariables].map(v => v.label)
      );
      //**ami  */
      if (this.sort == "Alphabetical") {
        console.log("sorting by Alphabetical");
        return inputVariables;
      } else if (this.sort == "Domain") {
        console.log("sorting by Domain");
        return inputVariables.reverse();
      } else if (this.sort == "Variable") {
        console.log("sorting by Variable");
        return inputVariables.sort();
      } else if (this.sort == "Selection") {
        console.log("sorting by Selection");
        return inputVariables.reverse();
      }
    },
    userChangedVariable() {
      this.$emit("userChangedInputVariable", true);
    },
    comparePredefinedRanges(ranges) {
      this.$emit("comparePredefinedRanges", ranges);
    },
    savePredefinedRanges(ranges) {
      this.$emit("savePredefinedRanges", ranges);
    }
  }
};
</script>

<style scoped>
.horizontal {
  display: flex;
}

.xscrollable {
  overflow-x: auto;
  overflow-y: hidden;
}
.scrollable::-webkit-scrollbar {
  display: none;
}
</style>
