<template>
  <div class="xscrollable px-2">
    <v-card class="d-flex flex-row pb-1">
      
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
    items: [{ title: "Type" }, { title: "Variable" }, { title: "Domain" }]
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

  
  methods: {
    reOrderVariables: function(newTitle, inputVariables) {
      function getLabel(v) {
        if ("parentLabel" in v) {
          return v.parentLabel;
        }
        return v.label;
      }
      console.log(newTitle, "calling reorderVariables", inputVariables);
      // let tmpArry=[]
      // tmpArry.push(inputVariables[2]);
      // tmpArry.push(inputVariables[1]);
      // tmpArry.push(inputVariables[3]);
      // tmpArry.push(inputVariables[0]);
      // inputVariables=tmpArry;
      if (newTitle == "Domain") {
        
        inputVariables.sort(function(a, b) {
          if (a.category > b.category) return -1;
          if (a.category < b.category) return 1;
          return 0;
        });
        return inputVariables;
      }
      if (newTitle == "Variable") {
        
        inputVariables.sort(function(a, b) {
          
          if (getLabel(a) < getLabel(b) ) return -1; // <
          if (getLabel(a) > getLabel(b)) return 1; // >

         
        });
        return inputVariables;
      }
    
      else {
        return inputVariables; // by Type
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
