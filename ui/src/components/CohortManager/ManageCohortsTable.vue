<template>
  <div>
    <v-container fluid fill-width class="ma-0 pa-0">
      <v-row class="ma-0 pa-0">
        <v-col cols="12" class="ma-0 pa-0">
          <v-card color="#eeeeee" class="pt-1">
            <v-card-title class="primary--text pl-3 py-2"
			  >{{ title }}
	      <v-chip label color="primary" class="white--text title mr-2 ml-4"
		      >{{ cohorts ? cohorts.length : 0 }}</v-chip>

              <v-spacer />
              <v-toolbar-items>
              </v-toolbar-items>
            </v-card-title>
          </v-card>
        </v-col>
      </v-row>
    </v-container>

    <v-sheet v-show="expanded" color="white" class="rounded-lg shadow">
      <!-- no cohorts selected -->
      <v-container
        v-if="!cohorts || cohorts.length == 0"
        fluid
        fill-width
        class="ma-0 pa-0"
      >
        <v-row class="ma-0 pa-0">
          <v-col cols="12" class="ma-0 pa-0">
            <div column align-center justify-center fill-width class="py-3">
              <v-subheader class="title primary--text text--lighten-5">
                No cohorts
              </v-subheader>
            </div>
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
        :disable-pagination="disablePagination"
        :hide-default-footer="disablePagination"
	class="cohorts"
	dense
        @click:row="rowClicked"
      >
        <template v-slot:item.data-table-select="{ isSelected, select }">
          <td class="pa-0 ma-0" justify="center" align="center">
            <v-tooltip v-if="checkboxTooltip" bottom color="primary">
              <template v-slot:activator="{ on: tooltip }">
                <v-simple-checkbox
                  :value="isSelected"
                  class="pa-0 ma-0"
                  dense
                  hide-details
                  v-on="{ ...tooltip }"
                  @input="select($event)"
                />
              </template>
              <span>{{ checkboxTooltip }}</span>
            </v-tooltip>
            <v-simple-checkbox
              v-else
              :value="isSelected"
              class="pa-0 ma-0"
              dense
              hide-details
              @input="select($event)"
            />
          </td>
        </template>

        <template v-slot:item.label="{ item }">
          <td class="subtitle-1 text-xs-left">
	    <span v-if="cohort && (item.id == cohort.id)" class="font-weight-bold"">{{item.label}}</span>

            <span v-else v-html="item.label"></span>
          </td>
        </template>

        <template v-slot:item.size="{ item }">
          <td class="subtitle-1 text-xs-center align-center" align-center>
	    <span v-if="cohort && (item.id == cohort.id)" class="font-weight-bold">
	      {{ item.subject_ids ? item.subject_ids.length : '?' }}
	    </span>
	    <span v-else>
	      {{ item.subject_ids ? item.subject_ids.length : '?' }}
	    </span>
          </td>
        </template>

        <template v-slot:item.query_string="{ item }">
          <td class="subtitle-1 text-xs-left">{{ item.query_string }}</td>
        </template>

	<template v-slot:item.actions="{ item }">
          <td class="subtitle-1 text-xs-center">
	    <!-- edit -->
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
		<v-icon v-if="cohort && (item.id == cohort.id)" color="white" @click="editCohort(item)">edit</v-icon>
		<v-icon v-else @click="editCohort(item)">edit</v-icon>
              </template>
              <span class="subtitle-1"
                    >Edit cohort
                }}
	      </span>
            </v-tooltip>

	    <!--delete -->
            <v-tooltip top color="primary">
              <template v-slot:activator="{ on: tooltip }">
		<delete-cohort-icon-dialog :cohort="item" :selected="cohort && (item.id == cohort.id)" @cohortDeleted="cohortDeleted"></delete-cohort-icon-dialog>
              </template>
              <span class="subtitle-1"
                    >Delete cohort
                }}
	      </span>
            </v-tooltip>

	  </td>
        </template>

        <template v-slot:item.color="{ item }">
          <v-chip small :color="item.color" class="my-1" />
        </template>
      </v-data-table>

      <v-container fluid class="pb-2 px-1">
        <v-row class="ma-0 pa-0 align-center">
          <v-col cols="4" class="ma-0 pa-0" align="center">

	    <v-btn class="primary text--white ma-0 px-2 py-0"
		   @click="newCohort"
		   >New Cohort</v-btn>
	  </v-col>
	  
	  <v-col cols="4" class="ma-0 pa-0" align="center">
	    <save-cohort-btn-dialog :cohorts="cohorts" @cohortSaved="cohortSaved"></save-cohort-btn-dialog>
	  </v-col>
	  
	  <v-col cols="4" class="ma-0 pa-0" align="center">
	    <analysis-summary-btn-dialog :collection-id="collectionId"></analysis-summary-btn-dialog>
	  </v-col>
	</v-row>
      </v-container>
      
      <div
        v-if="reportMaxOverlap || reportMaxSelectedOverlap"
        class="ma-0 pa-3"
        style="height: 3em"
      >
        <div v-if="reportMaxOverlap && maxOverlap" class="pa-0">
          <v-icon class="pa-1" color="warning" medium>warning</v-icon>
          <span>{{ 'WARNING: ' + maxOverlap.descr }}</span>
        </div>
        <div v-if="reportMaxSelectedOverlap && maxSelectedOverlap" class="pa-0">
          <v-icon class="pa-1" color="warning" medium>warning</v-icon>
          <span>{{ 'WARNING: ' + maxSelectedOverlap.descr }}</span>
        </div>
      </div>
    </v-sheet>

    <v-dialog v-model="analysisDialog" width="500">
      <v-card class="rounded-lg">
        <v-card-title color="white" primary-title>
          <v-icon color="primary">grid_on</v-icon>
          <span class="primary--text text--darken-3 title pl-2"
            >Proceed to Summary Matrix</span
          >
        </v-card-title>

        <v-card-text class="primary primary--text text--lighten-5 pt-4">
          Are you sure you want to leave the Cohort Manager and go to the
          Summary Matrix?
        </v-card-text>

        <v-divider></v-divider>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn text color="primary" @click="analysisDialog = false">
            <v-icon left>close</v-icon> No
          </v-btn>
          <v-btn
            color="primary"
            @click="routeToAnalysisSummary"
          >
            Yes</v-btn
          >
        </v-card-actions>
      </v-card>
    </v-dialog>

  </div>
</template>

<script>
import { mapActions, mapState, mapGetters } from 'vuex';
import { actions, state, getters } from '@/store/modules/cohortManager/types';

import { format } from 'd3-format';
import DeleteCohortIconDialog from '@/components/CohortManager/DeleteCohortIconDialog.vue';
import SaveCohortBtnDialog from '@/components/CohortManager/SaveCohortBtnDialog.vue';
import AnalysisSummaryBtnDialog from '@/components/DataExplorer/AnalysisSummaryBtnDialog.vue';

export default {
  components: {
    DeleteCohortIconDialog,
    SaveCohortBtnDialog,
    AnalysisSummaryBtnDialog,
  },
  props: {
    title: {
      type: String,
      required: false,
      default: 'MANAGE COHORTS',
    },
    cohorts: {
      type: Array,
      required: true,
    },
    collectionId: {
      type: Number,
      required: true,
    },
    // cohorts to select on initial load
    selectCohorts: {
      type: Array,
      required: false,
      default: x => [],
    },
    showSelect: {
      type: Boolean,
      required: false,
      default: false,
    },
    showColors: {
      type: Boolean,
      required: false,
      default: false,
    },
    reportMaxSelectedOverlap: {
      type: Boolean,
      required: false,
      default: false,
    },
    reportMaxOverlap: {
      type: Boolean,
      required: false,
      default: false,
    },
    disablePagination: {
      type: Boolean,
      required: false,
      default: false,
    },
    checkboxTooltip: {
      type: String,
      required: false,
    },
  },
  data() {
    return {
      selected: [],
      expanded: true,
      maxOverlap: null,
      maxSelectedOverlap: null,
      analysisDialog: false,
      selectedRow: null,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      cohort: state.COHORT,
      collection: state.COLLECTION,
    }),
    headers() {
      var hdrs = [];
      hdrs.push({
        text: 'Cohort Name',
        value: 'label',
        class: 'text-subtitle-1 font-weight-bold',
      });

      if (this.showColors) {
        hdrs.push({
          text: 'Color',
          value: 'color',
          class: 'text-subtitle-1 font-weight-bold',
        });
      }

      hdrs.push({
        text: 'Subjects',
        value: 'size',
        class: 'text-subtitle-1 font-weight-bold',
      });

//      hdrs.push({
//        text: 'Query',
//        value: 'query_string',
//        class: 'text-subtitle-1 font-weight-bold',
//      });

      hdrs.push({
        text: 'Actions',
        value: 'actions',
        class: 'text-subtitle-1 font-weight-bold',
      });

      return hdrs;
    },
  },
  watch: {
    selected(nsel) {
      this.$emit('selectedCohorts', nsel);
      // compute and store maximum overlap between any two _selected_ cohorts
      if (this.reportMaxSelectedOverlap) {
        var max_o = this.computeMaxOverlap(nsel);
        this.maxSelectedOverlap = max_o;
        this.$emit('maxSelectedOverlap', max_o);
      }
    },
  },
  created() {
    // compute and store maximum overlap between any two cohorts
    if (this.reportMaxOverlap) {
      var max_o = this.computeMaxOverlap(this.cohorts);
      this.maxOverlap = max_o;
      this.$emit('maxOverlap', max_o);
    }
    if (this.selectCohorts) {
      this.selected = this.selectCohorts;
    }
  },
  methods: {
    computeMaxOverlap(cohorts) {
      var overlaps = this.computeOverlaps(cohorts);
      var sortedOverlaps = overlaps.sort((a, b) => b.max_pct - a.max_pct);

      if (overlaps.length > 0) {
        return sortedOverlaps[0];
      } else {
        return null;
      }
    },
    computeOverlaps(cohorts) {
      var overlaps = [];

      // build subject id index for each cohort
      var subjIdsH = [];
      cohorts.forEach(c => {
        var h = {};
        c.subject_ids.forEach(s => {
          h[s] = 1;
        });
        subjIdsH.push(h);
      });

      // perform all vs. all comparison (N^2)
      var nc = cohorts.length;
      for (var i = 0; i < nc; ++i) {
        for (var j = i + 1; j < nc; ++j) {
          // compare i and j
          var n_in_both = 0;
          cohorts[i].subject_ids.forEach(s => {
            if (s in subjIdsH[j]) {
              ++n_in_both;
            }
          });
          if (n_in_both == 0) {
            continue;
          }
          var a_pct = (n_in_both / cohorts[i].subject_ids.length) * 100.0;
          var b_pct = (n_in_both / cohorts[j].subject_ids.length) * 100.0;
          var descr = null;
          var max_pct = null;
          var plural_subject = n_in_both > 1 ? 'subjects' : 'subject';
          var plural_is = n_in_both > 1 ? 'are' : 'is';

          if (a_pct > b_pct) {
            max_pct = a_pct;
            descr =
              n_in_both +
              ' ' +
              plural_subject +
              ' (' +
              format('.1f')(a_pct) +
              "%) from cohort '" +
              cohorts[i].label +
              "' " +
              plural_is +
              " also in cohort '" +
              cohorts[j].label +
              "'";
          } else {
            max_pct = b_pct;
            descr =
              n_in_both +
              ' ' +
              plural_subject +
              ' (' +
              format('.1f')(b_pct) +
              "%) from cohort '" +
              cohorts[j].label +
              "' " +
              plural_is +
              " also in cohort '" +
              cohorts[i].label +
              "'";
          }
          overlaps.push({
            a: cohorts[i],
            b: cohorts[j],
            a_pct: a_pct,
            b_pct: b_pct,
            max_pct: max_pct,
            n_in_both: n_in_both,
            descr: descr,
          });
        }
      }
      return overlaps;
    },
    rowClicked(newCohort, row) {
      this.$emit('selectedCohort', newCohort);
      if (this.selectedRow != null) this.selectedRow.select(false);
      row.select(true);
      this.selectedRow = row;
    },
    editCohort(cohort) {
      console.log("editCohort called on " + cohort);
    },
    newCohort() {
      if (this.selectedRow != null) this.selectedRow.select(false);
      this.$emit('newCohort')
    },
    cohortSaved() {
    },
    cohortDeleted() {
      if (this.selectedRow != null) this.selectedRow.select(false);
      this.$emit('newCohort')
    },
    routeToAnalysisSummary() {
      this.$router.push(`summary?collection=${this.collectionId}`);
    },
  },
};
</script>

<style>
div.cohorts tr.v-data-table__selected {
  background-color: #3f51b5 !important;
  color: #ffffff !important;
}
</style>
