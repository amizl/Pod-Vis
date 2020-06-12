<template>
  <v-container>
    <v-flex>
      <svg
        id="greenbox"
        ref="rect"
        :width="canvasWidth"
        :height="canvasHeight"
        style="background: white"
      ></svg>
    </v-flex>
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
import { getObservationVariableNames } from '@/utils/helpers';

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
        top: 60,
        right: 100,
        bottom: 10,
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
    };
  },
  computed: {
    ...mapState('dataSummary', {
      collection: state.COLLECTION,
      collectionSummaries: state.COLLECTION_SUMMARIES,
      firstVisit: state.FIRST_VISIT,
      lastVisit: state.LAST_VISIT,
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
      this.updateCanvas();
    },
    firstVisit() {
      this.updateCanvas();
    },
    lastVisit() {
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
    updateCanvas() {
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );
      this.eventCount = this.uniqueEvents.length;

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
          // console.log('Count: ' + d[2] + ' z: ' + val);
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
        .attr('y', margin.top - 40)
        .text(this.visitVariable)
        .style('font-size', 25);

      // Add legend to the plot
      var circInt = this.maxGroupCount / 4;

      var cirCounts = [];
      for (let index = 0; index < 5; index++) {
        cirCounts.push(Math.round(index * circInt) + 1);
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

      // unused
      var highlightRow = function(var_id, color) {
        mysvg
          .append('g')
          .append('rect')
          .attr('x', margin.left)
          .attr('y', y(var_id) + margin.top)
          .attr('width', width - margin.left - margin.right)
          .attr('height', y_bw)
          .style('fill', color)
          .style('opacity', '0.4')
          .attr('stroke', 'none');
      };

      var highlightColHeading = function(visit, color, chart, is_first) {
        var cx = x(visit) + margin.left;
        var cy = margin.top - y.bandwidth();

        var g = mysvg.append('g');
        var colRect = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', color)
          .style('opacity', '0.4')
          .attr('stroke', 'black');
      };

      var addDraggableHighlightCol = function(visit, color, chart, is_first) {
        var cx = x(visit) + margin.left;
        var cy = margin.top;

        var g = mysvg.append('g');
        var colRect = g
          .append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', height)
          .style('fill', color)
          .style('opacity', '0.4')
          .attr('stroke', 'black');

        // enable dragging
        var min_x = margin.left;
        var max_x = margin.left + width - x.bandwidth();
        var xoffset = 0;

        var start_drag_fn = function(d) {
          xoffset = d3.event.x - d3.select(this).attr('x');
        };

        // TODO - do not allow one endpoint to be dragged over the other
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
            if (chart.lastVisit) {
              var lvx = x(chart.lastVisit) + margin.left;
              if (new_x > lvx - x_bw) {
                new_x = lvx - x_bw;
              }
            }
          }
          // don't allow last visit to go past first visit
          else {
            if (chart.firstVisit) {
              var lvx = x(chart.firstVisit) + margin.left;
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
            chart.setFirstVisit(visit);
          } else {
            chart.setLastVisit(visit);
          }
        };

        var dh = d3
          .drag()
          .on('start', start_drag_fn)
          .on('drag', on_drag_fn)
          .on('end', drag_end_fn);
        dh(colRect);
      };

      // highlight saved first/last visit
      if (this.collection.observation_variables_list.length > 0) {
        var ov = this.collection.observation_variables_list[0];
        if (this.visitVariable == 'Visit Event') {
          if (ov.first_visit_event) {
            highlightColHeading(
              ov['first_visit_event'],
              colors['firstVisit'],
              this,
              true
            );
          }
          if (ov.last_visit_event) {
            highlightColHeading(
              ov['last_visit_event'],
              colors['lastVisit'],
              this,
              true
            );
          }
        } else {
          if (ov.first_visit_num) {
            highlightColHeading(
              ov['first_visit_num'],
              colors['firstVisit'],
              this,
              true
            );
          }
          if (ov.last_visit_num) {
            highlightColHeading(
              ov['last_visit_num'],
              colors['lastVisit'],
              this,
              true
            );
          }
        }
      }

      // highlight first and last selections
      if (this.firstVisit) {
        addDraggableHighlightCol(
          this.firstVisit,
          colors['firstVisit'],
          this,
          true
        );
      }
      if (this.lastVisit) {
        addDraggableHighlightCol(
          this.lastVisit,
          colors['lastVisit'],
          this,
          false
        );
      }
    },
    ...mapMutations('dataSummary', {
      setFirstVisit: actions.SET_FIRST_VISIT,
      setLastVisit: actions.SET_LAST_VISIT,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
