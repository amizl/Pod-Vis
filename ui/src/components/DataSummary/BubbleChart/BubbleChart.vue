<template>
  <v-flex>
    <svg
      id="greenbox"
      ref="rect"
      :width="canvasWidth"
      :height="canvasHeight"
      style="background: white"
    ></svg>
  </v-flex>
</template>

<script>
// Data Store
import { mapState } from 'vuex';
import { state } from '@/store/modules/dataSummary/types';
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
  data() {
    return {
      isLoading: true,
      haveDimensions: false,
      canvasWidth: 1200,
      canvasHeight: 1000,
      margin: {
        top: 70,
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
    };
  },
  computed: {
    ...mapState('dataSummary', {
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
    h() {
      return this.canvasHeight - this.margin.top - this.margin.bottom;
    },
    w() {
      return this.canvasWidth - this.margin.left - this.margin.right;
    },
  },
  watch: {
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
    updateCanvas() {
      // Identify the unique events
      this.uniqueEvents = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 0)
      );
      this.eventCount = this.uniqueEvents.length;

      // Identufy the unique tests
      this.uniqueTests = this.getUniqueList(
        this.getColumn(this.collectionSummaries[this.visitVariable], 1)
      );
      this.testCount = this.uniqueTests.length;

      var testGroupCounts = this.getColumn(
        this.collectionSummaries[this.visitVariable],
        2
      );
      this.minGroupCount = Math.min(...testGroupCounts);
      this.maxGroupCount = Math.max(...testGroupCounts);

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
        .range([height, margin.top]);

      var x_bw = x.bandwidth();
      var x_hbw = x_bw / 2;
      var y_bw = y.bandwidth();
      var y_hbw = y_bw / 2;

      // Calculate the maximum size of the circle for bubble
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

      mysvg
        .append('g')
        .attr('transform', 'translate(' + margin.left + ', 0)')
        .call(d3.axisLeft(y));

      mysvg
        .append('g')
        .selectAll('dot')
        .data(this.collectionSummaries[this.visitVariable])
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
        .style('opacity', '0.7')
        .attr('stroke', 'black');

      mysvg
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('x', width / 2 + 200)
        .attr('y', margin.top - 40)
        .text(this.visitVariable)
        .style('font-size', 25);

      // Add legend to the plot
      var circInt = this.maxGroupCount / 5;

      var cirCounts = [];
      for (let index = 0; index < 5; index++) {
        cirCounts.push(Math.round(index * circInt) + 1);
      }

      // Draw a rectangle around the legend
      mysvg
        .append('g')
        .append('rect')
        .attr('x', width + margin.left + 5)
        .attr('y', margin.top * 2)
        .attr('width', max_radius * 5)
        .attr('height', max_radius * 10)
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
        .attr('cx', width + margin.left + 20)
        .attr('cy', function(d, i) {
          var val = (5 - i) * max_radius * 1.6 + margin.top * 2;
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
        .attr('x', width + margin.left + max_radius * 2 + 20)
        .attr('y', function(d, i) {
          var val = (5 - i) * max_radius * 1.6 + margin.top * 2 + 5;
          return val;
        })
        .style('font-size', 10)
        .text(function(d) {
          return d;
        });

      var highlightCol = function(visit, color) {
        mysvg
          .append('g')
          .append('rect')
          .attr('x', x(visit) + margin.left)
          .attr('y', margin.top)
          .attr('width', x.bandwidth())
          .attr('height', height - margin.top)
          .style('fill', color)
          .style('opacity', '0.4')
          .attr('stroke', 'none');
      };

      // highlight first and last selections
      if (this.firstVisit) {
        highlightCol(this.firstVisit, 'lightgreen');
      }
      if (this.lastVisit) {
        highlightCol(this.lastVisit, 'lightblue');
      }
    },
  },
};
</script>

<style lang="scss" scoped></style>
