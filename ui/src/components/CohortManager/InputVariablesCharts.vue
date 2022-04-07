<template>
  <div class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
      <!-- 
           <v-card
        v-for="(inputVariable, index) in reOrderVariables(newTitle, [...inputVariables])"
        :key="'ivcc-' + inputVariable.id"
        :class="index > 0 ? 'ml-2 pb-1' : 'pb-1'"
      >
      -->
      <!--
      <div>computed sort -- {{ this.sort }} --</div>

      <div>store sort {{ $store.state.cohortManager.sort }}</div>
-->
      <v-card
        v-for="(inputVariable, index) in reOrderVariables(this.sort, [
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
   // newTitle: null
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
  watch: {
    reOrderVariables(newTitle, inputVariables) {
      this.$emit("reOrderVariables");
    }
  },
  methods: {
    reOrderVariables: function(newTitle, inputVariables) {
      console.log(newTitle, "calling reorderVariables", inputVariables);
      // let tmpArry=[]
      // tmpArry.push(inputVariables[2]);
      // tmpArry.push(inputVariables[1]);
      // tmpArry.push(inputVariables[3]);
      // tmpArry.push(inputVariables[0]);
      // inputVariables=tmpArry;
      if (newTitle == "Selection") {
        inputVariables.sort(function(a, b) {
          if (a.category > b.category) return -1;
          if (a.category < b.category) return 1;
          return 0;
        });
        return inputVariables;
      }
      if (newTitle == "Domain") {
        inputVariables.sort(function(a, b) {
          if (a.label > b.label) return -1; // <
          if (a.label < b.label) return 1; // >
          return 0;
        });
        return inputVariables;
      }
      if (newTitle == "Variable") {
        inputVariables.sort(function(a, b) {
          if (a.data_category < b.data_category) return -1; // <
          if (a.data_category > b.data_category) return 1; // >
          return 0;
        });
        return inputVariables;
      } else {
        return inputVariables;
      }
      /*
      newTitle = this.sort;
      
      if (this.sort == "Alphabetical") {
        console.log("sorting by Alphabetical");
        console.log(
          this.sort +
            " test " +
            newTitle +
            " " +
            [...inputVariables].map(v => v.category)
        );
        return inputVariables;
      } else if (this.sort == "Domain") {
        console.log("sorting by Domain");
        console.log(
          this.sort +
            " test " +
            newTitle +
            " " +
            [...inputVariables].map(v => v.category).reverse()
        );
        return inputVariables.reverse();
      } else if (this.sort == "Variable") {
        console.log("sorting by Variable");
        console.log(
          this.sort +
            " test " +
            newTitle +
            " " +
            [...inputVariables].map(v => v.category)
        );
        return inputVariables.sort();
      } else if (this.sort == "Selection") {
        console.log("sorting by Selection");
        console.log(
          this.sort +
            " test " +
            newTitle +
            " " +
            [...inputVariables].map(v => v.category)
        );
        return inputVariables.reverse();
      }
      */
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
