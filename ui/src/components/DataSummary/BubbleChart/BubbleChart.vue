<template>
  <v-container fluid fill-width>
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <svg
          id="greenbox"
          ref="rect"
          :width="canvasWidth"
          :height="canvasHeight"
          style="background: white"
        ></svg>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
// Data Store
import { mapState, mapMutations } from 'vuex';
import { state, actions } from '@/store/modules/dataSummary/types';
// D3 Modules
import * as d3 from 'd3';
import { max } from 'd3-array';
import { select } from 'd3-selection';
import { scaleLinear, scaleBand, scaleOrdinal } from 'd3-scale';
import 'd3-transition';
import { axisBottom, axisLeft } from 'd3-axis';
import { schemeCategory10 } from 'd3-scale-chromatic';
// Directives
import resize from 'vue-resize-directive';
import { colors } from '@/utils/colors';
// Util
import {
  getObservationVariableIds,
  getObservationVariableNames,
} from '@/utils/helpers';

export default {
  directives: {
    resize,
    xaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
    },
    yaxis(el, binding) {
      const axisMethod = binding.value;
      select(el).call(axisMethod);
    },
  },
  props: {
    varOpacity: {
      type: String,
      required: true,
    },
    collectionVarOpacity: {
      type: String,
      required: true,
    },
    hideUnselectedVars: {
      type: Boolean,
      required: false,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      defaultCanvasWidth: 1200,
      defaultCanvasHeight: 1000,
      minPxPerCol: 18,
      maxPxPerRow: 40,
      margin: {
        top: 70,
        right: 100,
        bottom: 40,
        left: 220,
      },
      selected: [],
      container: null,
      dimension: null,
      group: [],
      data: [],
      uniqueEvents: [],
      uniqueTests: [],
      minGroupCount: 0,
      maxGroupCount: 0,
      testCount: 0,
      eventCount: 0,
      colors: colors,
      collectionVarNames: {},
      firstVisitHandle: null,
      lastVisitHandle: null,
    };
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collectionSummaries: state.COLLECTION_SUMMARIES,
      firstVisits: state.FIRST_VISITS,
      lastVisits: state.LAST_VISITS,
      visitVariable: state.VISIT_VARIABLE,
    }),
    domain() {
      // return Array(this.min, this.max);
      return [0, this.eventCount]; // [min, max]
    },
    range() {
      return Array(0, this.canvasHeight);
    },
    scale() {
      return d3
        .scaleLinear()
        .domain(this.domain)
        .range(this.range)
        .nice(); // rounds domain to nice numbers
    },
    canvasWidth() {
      var nCols = this.uniqueEvents.length;
      var width =
        this.defaultCanvasWidth - this.margin.left - this.margin.right;
      var pxPerCol = width / nCols;
      if (pxPerCol < this.minPxPerCol) {
        return this.minPxPerCol * nCols + this.margin.left + this.margin.right;
      } else {
        return this.defaultCanvasWidth;
      }
    },
    canvasHeight() {
      var nRows = this.uniqueTests.length;
      var pxPerRow =
        (this.defaultCanvasHeight - this.margin.top - this.margin.bottom) /
        nRows;
      if (pxPerRow > this.maxPxPerRow) {
        var calcCanvasHeight =
          this.maxPxPerRow * nRows + this.margin.top + this.margin.bottom;
        return calcCanvasHeight;
      } else {
        return this.defaultCanvasHeight;
      }
    },
    h() {
      return this.canvasHeight - this.margin.top - this.margin.bottom;
    },
    w() {
      return this.canvasWidth - this.margin.left - this.margin.right;
    },
  },
  watch: {
    hideUnselectedVars() {
      this.updateCanvas();
    },
    visitVariable() {
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );
      this.firstVisitHandle = null;
      this.lastVisitHandle = null;
      this.updateCanvas();
    },
    firstVisits() {
      this.updateCanvas();
    },
    lastVisits() {
      this.updateCanvas();
    },
  },
  mounted() {
    this.updateCanvas();
  },
  methods: {
    getColumn(anArray, columnNumber) {
      return anArray.map(function(row) {
        return row[columnNumber];
      });
    },
    getUniqueList(anArray) {
      var unique = anArray.filter((v, i, a) => a.indexOf(v) === i);
      return unique;
    },
    getCollectionSummaries() {
      if (this.hideUnselectedVars) {
        var summaries = [];
        var collectionVarNames = this.collectionVarNames;
        this.collectionSummaries[this.visitVariable].forEach(s => {
          if (s[1] in collectionVarNames) {
            summaries.push(s);
          }
        });
        return summaries;
      } else {
        return this.collectionSummaries[this.visitVariable];
      }
    },
    setAllFirstVisits(visit) {
      var varIds = getObservationVariableIds(this.collection);
      var newFirstVisits = {};
      varIds.forEach(id => {
        newFirstVisits[id] = visit;
      });
      this.firstVisitHandle = visit;
      this.setFirstVisits(newFirstVisits);
    },
    setAllLastVisits(visit) {
      var varIds = getObservationVariableIds(this.collection);
      var newLastVisits = {};
      varIds.forEach(id => {
        newLastVisits[id] = visit;
      });
      this.lastVisitHandle = visit;
      this.setLastVisits(newLastVisits);
    },
    // TODO - move these two methods to actions.js?
    setFirstVisit(varId, visit) {
      var newFirstVisits = {};
      Object.keys(this.firstVisits).forEach(id => {
        newFirstVisits[id] = this.firstVisits[id];
      });
      newFirstVisits[varId] = visit;
      this.setFirstVisits(newFirstVisits);
    },
    setLastVisit(varId, visit) {
      var newLastVisits = {};
      Object.keys(this.lastVisits).forEach(id => {
        newLastVisits[id] = this.lastVisits[id];
      });
      newLastVisits[varId] = visit;
      this.setLastVisits(newLastVisits);
    },
    // set first visit handle based on majority vote
    setVisitHandle(is_first) {
      var varIds = getObservationVariableIds(this.collection);
      var visits = {};
      varIds.forEach(vid => {
        var v = is_first ? this.firstVisits[vid] : this.lastVisits[vid];
        if (v != null) {
          if (v in visits) {
            visits[v] += 1;
          } else {
            visits[v] = 1;
          }
        }
      });
      // sort by decreasing visit count
      var sortFn = function compare(a, b) {
        var ca = visits[a];
        var cb = visits[b];
        return cb - ca;
      };
      var selectedVisits = Object.keys(visits).sort(sortFn);
      if (is_first) {
        if (selectedVisits[0] == null) {
          this.firstVisitHandle = this.uniqueEvents[0];
          this.setAllFirstVisits(this.uniqueEvents[0]);
        } else {
          this.firstVisitHandle = selectedVisits[0];
          this.setAllFirstVisits(selectedVisits[0]);
        }
      } else {
        if (selectedVisits[0] == null) {
          this.lastVisitHandle = this.uniqueEvents[
            this.uniqueEvents.length - 1
          ];
          this.setAllLastVisits(
            this.uniqueEvents[this.uniqueEvents.length - 1]
          );
        } else {
          this.lastVisitHandle = selectedVisits[0];
          this.setAllLastVisits(selectedVisits[0]);
        }
      }
    },

    updateCanvas() {
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );

      this.eventCount = this.uniqueEvents.length;
      // HACK for PPMI
      if (
        this.uniqueEvents.join(',') ==
        'BL,PW,SC,ST,U01,V01,V02,V03,V04,V05,V06,V07,V08,V09,V10,V11,V12,V13,V14,V15,V16'
      ) {
        this.uniqueEvents = [
          'SC',
          'BL',
          'U01',
          'V01',
          'V02',
          'V03',
          'V04',
          'V05',
          'V06',
          'V07',
          'V08',
          'V09',
          'V10',
          'V11',
          'V12',
          'V13',
          'V14',
          'V15',
          'V16',
          'PW',
          'ST',
        ];
      }
      // if events are all numeric, sort them numerically
      var numericEvents = true;
      this.uniqueEvents.forEach(e => {
        if (isNaN(e)) {
          numericEvents = false;
        }
      });
      if (numericEvents) {
        this.uniqueEvents = this.uniqueEvents
          .map(a => +a)
          .sort((a, b) => a - b);
      }

      // Compute firstLast and lastFirst visits
      // TODO - duplicated from VisitVariablesToolbar
      var varIds = getObservationVariableIds(this.collection);
      var firstLastVisit = null;
      var lastFirstVisit = null;
      var firstVisits = {};
      var lastVisits = {};

      varIds.forEach(v => {
        firstVisits[this.firstVisits[v]] = true;
        lastVisits[this.lastVisits[v]] = true;
      });

      this.uniqueEvents.forEach(e => {
        if (e in firstVisits) {
          lastFirstVisit = e;
        }
        if (firstLastVisit == null && e in lastVisits) {
          firstLastVisit = e;
        }
      });

      // Identify the unique tests
      var uniqueTests = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 1)
      )
        .sort()
        .reverse();

      var testGroupCounts = this.getColumn(
        this.collectionSummaries[this.visitVariable],
        2
      );
      this.minGroupCount = Math.min(...testGroupCounts);
      this.maxGroupCount = Math.max(...testGroupCounts);

      // lookup of variable names actually in the collection
      var collectionVarNames = getObservationVariableNames(this.collection);
      this.collectionVarNames = collectionVarNames;

      if (this.hideUnselectedVars) {
        var selectedUniqueTests = [];
        uniqueTests.forEach(t => {
          if (t in collectionVarNames) {
            selectedUniqueTests.push(t);
          }
        });
        uniqueTests = selectedUniqueTests;
      }
      this.uniqueTests = uniqueTests;

      // set the dimensions and margins of the graph
      var width = this.canvasWidth - this.margin.left - this.margin.right;
      var height = this.canvasHeight - this.margin.top - this.margin.bottom;

      var margin = {
        left: this.margin.left,
        right: this.margin.right,
        top: this.margin.top,
        bottom: this.margin.bottom,
      };

      const mysvg = d3.select('svg#greenbox');
      mysvg.selectAll('*').remove();

      mysvg
        .attr('width', width + margin.left + margin.right)
        .attr('height', height + margin.top + margin.bottom)
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')');

      var x = d3
        .scaleBand()
        .domain(this.uniqueEvents)
        .range([0, width]);

      var y = d3
        .scaleBand()
        .domain(this.uniqueTests)
        .range([height + margin.top, margin.top]);

      var x_bw = x.bandwidth();
      var x_hbw = x_bw / 2;
      var y_bw = y.bandwidth();
      var y_hbw = y_bw / 2;

      // Calculate the maximum size of the circle for bubble
      this.testCount = this.uniqueTests.length;
      var max_radius = height / (this.testCount * 2);
      var z = d3
        .scaleSqrt()
        .domain([this.minGroupCount, this.maxGroupCount])
        .range([1, max_radius * 0.8]);

      mysvg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .call(d3.axisTop(x))
        .selectAll('text')
        .attr('transform', 'translate(10, -5)rotate(-45)');

      var cvo = this.collectionVarOpacity;
      var vo = this.varOpacity;

      mysvg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', 0)')
        .call(d3.axisLeft(y))
        .selectAll('text')
        .style('opacity', function(d) {
          return d in collectionVarNames ? cvo : vo;
        });

      mysvg
        .append('g')
        .selectAll('dot')
        .data(this.getCollectionSummaries())
        .enter()
        .append('circle')
        .attr('cx', function(d) {
          var val = x(d[0]);
          return val + margin.left + x_hbw;
        })
        .attr('cy', function(d) {
          var val = y(d[1]) + y_hbw;
          // console.log('y: ' + val);
          return val;
        })
        .attr('r', function(d) {
          var val = z(d[2]);
          //  console.log('Count: ' + d[2] + ' z: ' + val);
          return val;
        })
        .style('fill', '#69b3a2')
        .style('opacity', function(d) {
          return d[1] in collectionVarNames ? cvo : vo;
        })
        .attr('stroke', 'black');

      mysvg
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width / 2 + 200)
        .attr('y', margin.top - 50)
        .text(this.visitVariable)
        .style('font-size', 25);

      // Add legend to the plot
      var circInt = (this.maxGroupCount - this.minGroupCount) / 4;

      var cirCounts = [];
      for (let index = 0; index < 5; index++) {
        cirCounts.push(Math.round(index * circInt) + this.minGroupCount);
      }

      // Draw a rectangle around the legend
      mysvg
        .append('g')
        .append('rect')
        .attr('x', width + margin.left + 10)
        .attr('y', margin.top)
        .attr('width', max_radius * 5)
        .attr('height', max_radius * 11)
        .style('fill', 'gray')
        .style('opacity', '0.4')
        .attr('stroke', 'black');

      // Create the circles for the legend
      mysvg
        .append('g')
        .selectAll('dot')
        .data(cirCounts)
        .enter()
        .append('circle')
        .attr('cx', width + margin.left + 30)
        .attr('cy', function(d, i) {
          var val = (5 - i) * max_radius * 1.8 + margin.top;
          return val;
        })
        .attr('r', function(d) {
          var val = z(d);
          // console.log("legend circle d=" + d + " val=" + val);
          return val;
        })
        .style('fill', '#69b3a2')
        .style('opacity', '0.7')
        .attr('stroke', 'black');

      // Append the text showing the count size
      mysvg
        .append('g')
        .selectAll('dot')
        .data(cirCounts)
        .enter()
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width + margin.left + max_radius * 2 + 30)
        .attr('y', function(d, i) {
          var val = (5 - i) * max_radius * 1.8 + margin.top + 5;
          return val;
        })
        .style('font-size', 12)
        .text(function(d) {
          return d;
        });

      var highlightCell = function(
        var_id,
        var_name,
        visit,
        color,
        chart,
        is_first
      ) {
        var cx = x(visit) + margin.left;
        var cy = y(var_name);

        var g = mysvg.append('g');
        var colRect = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', 'none')
          .style('opacity', '0.4')
          .attr('stroke', color)
          .attr('stroke-width', '3');
      };

      var addDraggableHighlight = function(
        var_id,
        var_name,
        visit,
        color,
        chart,
        is_first
      ) {
        var cx = x(visit) + margin.left;
        var cy = y(var_name);

        var g = mysvg.append('g');
        var colRect = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', color)
          .style('opacity', '0.4')
          .attr('stroke', 'black')
          .attr('stroke-width', '0.5');

        // enable dragging
        var min_x = margin.left;
        var max_x = margin.left + width - x.bandwidth();
        var xoffset = 0;

        var start_drag_fn = function(d) {
          xoffset = d3.event.x - d3.select(this).attr('x');
        };

        var on_drag_fn = function(d) {
          var new_x = d3.event.x - xoffset;
          if (new_x < min_x) {
            new_x = min_x;
          }
          if (new_x > max_x) {
            new_x = max_x;
          }
          // don't allow first visit to go past last visit
          if (is_first) {
            if (chart.lastVisits[var_id]) {
              var lvx = x(chart.lastVisits[var_id]) + margin.left;
              if (new_x > lvx - x_bw) {
                new_x = lvx - x_bw;
              }
            }
          }
          // don't allow last visit to go past first visit
          else {
            if (chart.firstVisits[var_id]) {
              var lvx = x(chart.firstVisits[var_id]) + margin.left;
              if (new_x < lvx + x_bw) {
                new_x = lvx + x_bw;
              }
            }
          }
          d3.select(this).attr('x', new_x);
        };

        var drag_end_fn = function(d) {
          // find nearest visit event/num and update/snap to grid
          var midpt = d3.select(this).attr('x') * 1.0 + x_hbw;
          var visitnum = Math.floor((midpt - min_x) / x_bw);
          if (visitnum < 0) {
            visitnum = 0;
          }
          if (visitnum >= chart.uniqueEvents.length) {
            visitnum = chart.uniqueEvents.length - 1;
          }
          var visit = chart.uniqueEvents[visitnum];
          if (is_first) {
            chart.setFirstVisit(var_id, visit);
          } else {
            chart.setLastVisit(var_id, visit);
          }
        };

        var dh = d3
          .drag()
          .on('start', start_drag_fn)
          .on('drag', on_drag_fn)
          .on('end', drag_end_fn);
        dh(colRect);
      };

      var addDraggableHandle = function(visit, color, chart, is_first) {
        var cx = x(visit) + margin.left;
        var cy = margin.top - y.bandwidth();

        var g = mysvg.append('g');
        var colRect1 = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', color)
          .style('fill-opacity', '0.6');

        var colRect2 = g
          .append('rect')
          .attr('x', cx)
          .attr('y', height + margin.top)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', color)
          .style('fill-opacity', '0.6');

        var colRect3 = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', height + y.bandwidth() * 2)
          .style('fill', 'none')
          .attr('stroke', 'black')
          .attr('stroke-width', '1')
          .attr('stroke-opacity', '0.7');

        // enable dragging
        var min_x = margin.left;
        var max_x = margin.left + width - x.bandwidth();
        var xoffset = 0;

        var start_drag_fn = function(d) {
          xoffset = d3.event.x - d3.select(this).attr('x');
        };

        var on_drag_fn = function(d) {
          var new_x = d3.event.x - xoffset;
          if (new_x < min_x) {
            new_x = min_x;
          }
          if (new_x > max_x) {
            new_x = max_x;
          }
          // don't allow first visit to go past first last visit
          if (is_first) {
            var lvx = x(firstLastVisit) + margin.left;
            if (new_x > lvx - x_bw) {
              new_x = lvx - x_bw;
            }
          }
          // don't allow last visit to go past last first visit
          else {
            var lvx = x(lastFirstVisit) + margin.left;
            if (new_x < lvx + x_bw) {
              new_x = lvx + x_bw;
            }
          }
          d3.select(colRect1.node()).attr('x', new_x);
          d3.select(colRect2.node()).attr('x', new_x);
          d3.select(colRect3.node()).attr('x', new_x);
        };

        var drag_end_fn = function(d) {
          // find nearest visit event/num and update/snap to grid
          var midpt = d3.select(this).attr('x') * 1.0 + x_hbw;
          var visitnum = Math.floor((midpt - min_x) / x_bw);
          if (visitnum < 0) {
            visitnum = 0;
          }
          if (visitnum >= chart.uniqueEvents.length) {
            visitnum = chart.uniqueEvents.length - 1;
          }
          var visit = chart.uniqueEvents[visitnum];
          d3.select(colRect1.node()).attr('x', x(visit) + margin.left);
          d3.select(colRect2.node()).attr('x', x(visit) + margin.left);
          if (is_first) {
            chart.setAllFirstVisits(visit);
          } else {
            chart.setAllLastVisits(visit);
          }
        };

        var dh = d3
          .drag()
          .on('start', start_drag_fn)
          .on('drag', on_drag_fn)
          .on('end', drag_end_fn);
        dh(colRect1);
        dh(colRect2);
      };

      var varIdToName = {};
      this.collection.observation_variables_list.forEach(ov => {
        varIdToName[ov['ontology']['id']] = ov['ontology']['label'];
      });

      // highlight saved first/last visit selections
      if (this.collection.observation_variables_list.length > 0) {
        var vvl =
          this.visitVariable == 'Visit Event' ? 'visit_event' : 'visit_num';
        this.collection.observation_variables_list.forEach(ov => {
          if (ov['first_' + vvl]) {
            highlightCell(
              ov['ontology']['id'],
              varIdToName[ov['ontology']['id']],
              ov['first_' + vvl],
              colors['firstVisit'],
              this,
              true
            );
          }
          if (ov['last_' + vvl]) {
            highlightCell(
              ov['ontology']['id'],
              varIdToName[ov['ontology']['id']],
              ov['last_' + vvl],
              colors['lastVisit'],
              this,
              false
            );
          }
        });
      }

      if (this.firstVisitHandle == null) {
        this.setVisitHandle(true);
      }
      if (this.lastVisitHandle == null) {
        this.setVisitHandle(false);
      }

      // highlight first and last selections for each variable
      varIds.forEach(vid => {
        var fv = this.firstVisits[vid];
        var lv = this.lastVisits[vid];
        if (fv) {
          addDraggableHighlight(
            vid,
            varIdToName[vid],
            fv,
            colors['firstVisit'],
            this,
            true
          );
        }
        if (lv) {
          addDraggableHighlight(
            vid,
            varIdToName[vid],
            lv,
            colors['lastVisit'],
            this,
            false
          );
        }
      });
      addDraggableHandle(
        this.firstVisitHandle,
        colors['firstVisit'],
        this,
        true
      );
      addDraggableHandle(
        this.lastVisitHandle,
        colors['lastVisit'],
        this,
        false
      );
    },
    ...mapMutations('dataSummary', {
      setFirstVisits: actions.SET_FIRST_VISITS,
      setLastVisits: actions.SET_LAST_VISITS,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
