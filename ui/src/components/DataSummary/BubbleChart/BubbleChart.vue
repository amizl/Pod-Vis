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

    <!-- tooltips for scale abbreviations -->
    <v-row v-if="canvasUpdated" class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-tooltip
          v-for="(cvt, index) in collectionVarTitles"
          :key="`vtsa-${index}`"
          top
          color="primary"
          :activator="cvt['node']"
        >
          <span> {{ cvt['name'] }} </span>
        </v-tooltip>
      </v-col>
    </v-row>

    <!-- tooltips for scale abbreviations -->
    <v-row v-if="canvasUpdated" class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-tooltip
          v-for="(sv, index) in Object.keys(rowCounts)"
          :key="`vtsa2-${index}`"
          top
          color="primary"
          :activator="rowCounts[sv]['node']"
        >
          <span> {{ rowCounts[scale]['descr'] }} </span>
        </v-tooltip>
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
import { select } from 'd3-selection';
import 'd3-transition';
// Directives
import resize from 'vue-resize-directive';
import {
  colors,
  getNumSubjectsColor,
  getNumSubjectsTextColor,
} from '@/utils/colors';
// Util
import {
  getObservationVariableIds,
  getObservationVariableAbbreviations,
  getObservationVariableAbbreviationToName,
  getObservationVariableAbbreviationToDescription,
  sortVisitEvents,
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
    useLongScaleNames: {
      type: Boolean,
      default: false,
    },
  },
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      canvasUpdated: false,
      defaultCanvasWidth: 1200,
      defaultCanvasHeight: 1000,
      minPxPerCol: 18,
      maxPxPerRow: 40,
      margin: {
        top: 70,
        right: 180,
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
      collectionVarAbbreviations: {},
      collectionVarAbbreviationToName: {},
      collectionVarAbbreviationToDescr: {},
      firstVisitHandle: null,
      lastVisitHandle: null,
      rowCounts: {},
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
    // link scale name, abbreviation to corresponding SVG text element
    collectionVarTitles() {
      var titles = [];
      Object.keys(this.collectionVarAbbreviations).forEach(a => {
        var name = this.useLongScaleNames
          ? this.collectionVarAbbreviationToDescr[a]
          : this.collectionVarAbbreviationToName[a];
        var node = document.getElementById(a);
        titles.push({ abbrev: a, name: name, node: node });
      });
      return titles;
    },
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
    useLongScaleNames() {
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
        var collectionVarAbbreviations = this.collectionVarAbbreviations;
        this.collectionSummaries[this.visitVariable].forEach(s => {
          if (s[1] in collectionVarAbbreviations) {
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
        }
      }
    },

    updateCanvas() {
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );

      this.eventCount = this.uniqueEvents.length;
      this.uniqueEvents = sortVisitEvents(this.uniqueEvents);

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
        3
      );
      this.minGroupCount = Math.min(...testGroupCounts);
      this.maxGroupCount = Math.max(...testGroupCounts);

      // lookup of variable names actually in the collection
      var collectionVarAbbreviations = getObservationVariableAbbreviations(
        this.collection
      );
      this.collectionVarAbbreviations = collectionVarAbbreviations;
      this.collectionVarAbbreviationToName = getObservationVariableAbbreviationToName(
        this.collection
      );
      this.collectionVarAbbreviationToDescr = getObservationVariableAbbreviationToDescription(
        this.collection
      );

      if (this.hideUnselectedVars) {
        var selectedUniqueTests = [];
        uniqueTests.forEach(t => {
          if (t in collectionVarAbbreviations) {
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

      // x-axis labeled by visit
      var x = d3
        .scaleBand()
        .domain(this.uniqueEvents)
        .range([0, width]);
      var nEvents = this.uniqueEvents.length;

      // y-axis labeled by variable/test name
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

      // rotate visit names by 45 degrees to fit longer visit names
      mysvg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ',' + margin.top + ')')
        .call(d3.axisTop(x))
        .selectAll('text')
        .attr('transform', 'translate(10, -5)rotate(-45)');

      var cvo = this.collectionVarOpacity;
      var vo = this.varOpacity;
      var use_long = this.useLongScaleNames;
      var cv2n = this.collectionVarAbbreviationToName;

      // display unselected variables/tests as grayed-out
      mysvg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', 0)')
        .call(d3.axisLeft(y))
        .selectAll('text')
        .text(function(d) {
          if (use_long) {
            return d in cv2n ? cv2n[d] : d;
          } else {
            return d;
          }
        })
        .style('opacity', function(d) {
          return d in collectionVarAbbreviations ? cvo : vo;
        })
        .attr('id', function(d) {
          return d;
        });

      // draw a circle for each scale, visit pair
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
          var val = z(d[3]);
          //  console.log('Count: ' + d[2] + ' z: ' + val);
          return val;
        })
        .style('fill', '#69b3a2')
        .style('opacity', function(d) {
          return d[1] in collectionVarAbbreviations ? cvo : vo;
        })
        .attr('stroke', 'black');

      // generate row counts, indexed by scale name
      // for now we're just going to take min(first_visit_count, last_visit_count)

      var varNameToId = {};
      this.collection.observation_variables_list.forEach(ov => {
        varNameToId[ov['ontology']['abbreviation']] = ov['ontology']['id'];
      });

      var vm = this;
      var rowCounts = {};
      var maxCount = 0;

      var countDescrFn = function(count, scale, which, visit) {
        return (
          count +
          ' subject(s) had a measurement for ' +
          scale +
          ' recorded at ' +
          which +
          ' visit ' +
          visit
        );
      };

      this.getCollectionSummaries().forEach(cs => {
        var visit = cs[0];
        var scale = cs[1];
        var count = cs[3];
        var scaleId = varNameToId[scale];
        var which = null;
        var other = null;

        if (vm.firstVisits[scaleId] == visit) {
          which = 'first';
          other = 'last';
        }
        if (vm.lastVisits[scaleId] == visit) {
          which = 'last';
          other = 'first';
        }

        // is this visit one of those selected for this variable?
        if (scale in collectionVarAbbreviations && which != null) {
          if (!(scale in rowCounts)) {
            rowCounts[scale] = {
              count: count,
              n_visits: 1,
              descr: countDescrFn(count, scale, which, visit),
              other: other,
              scale_id: scaleId,
            };
          } else {
            if (count < rowCounts[scale]['count']) {
              rowCounts[scale]['count'] = count;
              rowCounts[scale]['descr'] = countDescrFn(
                count,
                scale,
                which,
                visit
              );
            }
            rowCounts[scale]['n_visits'] += 1;
          }
        }
      });

      this.uniqueTests.forEach(t => {
        if (t in rowCounts) {
          var rc = rowCounts[t];
          // only 1 visit found means no subjects with first + last
          if (nEvents > 1 && rc['n_visits'] < 2) {
            var other_visit =
              rc['other'] == 'first'
                ? vm.firstVisits[rc['scale_id']]
                : vm.lastVisits[rc['scale_id']];
            rc['count'] = 0;
            rc['descr'] =
              'no subjects had a measurement for ' +
              t +
              ' recorded at ' +
              rc['other'] +
              ' visit ' +
              other_visit;
          }
          if (rc['count'] > maxCount) {
            maxCount = rc['count'];
          }
        } else if (t in collectionVarAbbreviations) {
          rowCounts[t] = {
            count: 0,
            n_visits: 0,
            descr:
              'no subjects had a measurement for ' +
              t +
              ' recorded at the selected first or last visit',
          };
        }
      });

      this.rowCounts = rowCounts;
      var rcFontSize = 16;
      var qrcfs = Math.floor(rcFontSize / 4);

      // row counts - color-coded background rectangles
      mysvg
        .append('g')
        .selectAll('dot')
        .data(uniqueTests.filter(t => t in rowCounts))
        .enter()
        .append('rect')
        .attr('x', margin.left + width + 5)
        .attr('y', function(d) {
          return y(d);
        })
        .attr('width', rcFontSize * 5)
        .attr('height', y_bw)
        .attr('rx', qrcfs * 2)
        .attr('ry', qrcfs * 2)
        .style('fill', function(d) {
          return getNumSubjectsColor(rowCounts[d]['count']);
        })
        .style('stroke', 'white')
        .style('stroke-width', qrcfs);

      // row counts
      mysvg
        .append('g')
        .selectAll('dot')
        .data(uniqueTests.filter(t => t in rowCounts))
        .enter()
        .append('text')
        .attr('id', function(d) {
          return 'hr-' + d;
        })
        .attr('x', margin.left + width + 15)
        .attr('y', function(d) {
          return y(d) + y_hbw + qrcfs;
        })
        .text(function(d) {
          var ct = rowCounts[d]['count'];
          return ct == 0 ? '0' : '<= ' + ct;
        })
        .style('font-size', rcFontSize)
        .style('font-family', 'sans-serif')
        .style('color', function(d) {
          return getNumSubjectsTextColor(rowCounts[d]['count']);
        });

      Object.keys(rowCounts).forEach(k => {
        rowCounts[k]['node'] = document.getElementById('hr-' + k);
      });

      // display large visit variable caption (e.g., Visit Event vs. Visit Number)
      mysvg
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width / 2 + 200)
        .attr('y', margin.top - 50)
        .text(this.visitVariable)
        .style('font-size', 25);

      // Add legend to the plot showing reference circle sizes
      var circInt = (this.maxGroupCount - this.minGroupCount) / 4;

      var cirCounts = [];
      for (let index = 0; index < 5; index++) {
        cirCounts.push(Math.round(index * circInt) + this.minGroupCount);
      }

      // Draw a rectangle around the legend
      mysvg
        .append('g')
        .append('rect')
        .attr('x', width + margin.left + 90)
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
        .attr('cx', width + margin.left + 110)
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

      // Label legend circles with their sizes
      mysvg
        .append('g')
        .selectAll('dot')
        .data(cirCounts)
        .enter()
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width + margin.left + max_radius * 2 + 110)
        .attr('y', function(d, i) {
          var val = (5 - i) * max_radius * 1.8 + margin.top + 5;
          return val;
        })
        .style('font-size', 12)
        .text(function(d) {
          return d;
        });

      // Draw border around a single cell - used to indicate a selection saved in the database
      var highlightCell = function(var_id, var_name, visit, color, opacity) {
        var cx = x(visit) + margin.left;
        var cy = y(var_name);

        var g = mysvg.append('g');
        g.append('rect')
          .attr('x', cx)
          .attr('y', cy)
          .attr('width', x.bandwidth())
          .attr('height', y.bandwidth())
          .style('fill', 'none')
          .style('opacity', opacity)
          .attr('stroke', color)
          .attr('stroke-width', '3');
      };

      // Add a draggable highlight to a single cell
      var addDraggableHighlight = function(
        var_id,
        var_name,
        visit,
        color,
        opacity,
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
          .style('opacity', opacity)
          .attr('stroke', 'black')
          .attr('stroke-width', '0.5');

        // enable dragging
        var min_x = margin.left;
        var max_x = margin.left + width - x.bandwidth();
        var xoffset = 0;

        var start_drag_fn = function() {
          xoffset = d3.event.x - d3.select(this).attr('x');
        };

        var on_drag_fn = function() {
          var new_x = d3.event.x - xoffset;
          if (new_x < min_x) {
            new_x = min_x;
          }
          if (new_x > max_x) {
            new_x = max_x;
          }
          // don't allow first visit to go past last visit
          var lvx = null;
          if (is_first) {
            if (chart.lastVisits[var_id]) {
              lvx = x(chart.lastVisits[var_id]) + margin.left;
              if (new_x > lvx - x_bw) {
                new_x = lvx - x_bw;
              }
            }
          }
          // don't allow last visit to go past first visit
          else {
            if (chart.firstVisits[var_id]) {
              lvx = x(chart.firstVisits[var_id]) + margin.left;
              if (new_x < lvx + x_bw) {
                new_x = lvx + x_bw;
              }
            }
          }
          d3.select(this).attr('x', new_x);
        };

        var drag_end_fn = function() {
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

      // Add a draggable bar that can be used to change all first or last visits at the same time
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

        var start_drag_fn = function() {
          xoffset = d3.event.x - d3.select(this).attr('x');
        };

        var on_drag_fn = function() {
          var new_x = d3.event.x - xoffset;
          if (new_x < min_x) {
            new_x = min_x;
          }
          if (new_x > max_x) {
            new_x = max_x;
          }
          // don't allow first visit to go past first last visit
          var lvx = null;
          if (is_first) {
            lvx = x(firstLastVisit) + margin.left;
            if (new_x > lvx - x_bw) {
              new_x = lvx - x_bw;
            }
          }
          // don't allow last visit to go past last first visit
          else {
            lvx = x(lastFirstVisit) + margin.left;
            if (new_x < lvx + x_bw) {
              new_x = lvx + x_bw;
            }
          }
          d3.select(colRect1.node()).attr('x', new_x);
          d3.select(colRect2.node()).attr('x', new_x);
          d3.select(colRect3.node()).attr('x', new_x);
        };

        var drag_end_fn = function() {
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
        varIdToName[ov['ontology']['id']] = ov['ontology']['abbreviation'];
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
              colors['firstVisit-opacity']
            );
          }
          if (ov['last_' + vvl]) {
            highlightCell(
              ov['ontology']['id'],
              varIdToName[ov['ontology']['id']],
              ov['last_' + vvl],
              colors['lastVisit'],
              colors['lastVisit-opacity']
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
            colors['firstVisit-opacity'],
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
            colors['lastVisit-opacity'],
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
      this.canvasUpdated = true;
    },
    ...mapMutations('dataSummary', {
      setFirstVisits: actions.SET_FIRST_VISITS,
      setLastVisits: actions.SET_LAST_VISITS,
    }),
  },
};
</script>

<style lang="scss" scoped></style>
