<template lang="pug">
  svg(
    :width='width'
    :height='height'
  )
    g(:transform='translate')
</template>

<script>
/* eslint-disable */

import * as d3 from 'd3';

export default {
  data() {
    return {
      // dataset: [5,10,15,20,25, 6, 23, 6],
      testData: [{"measure":"updrs_17","total":4901,"1":3351,"2":848,"3":478,"4":202,"5":22},{"measure":"updrs_2","total":10158,"1":7189,"2":1779,"3":842,"4":307,"5":41},{"measure":"updrs_20f","total":10603,"1":9494,"2":677,"3":366,"4":59,"5":7},{"measure":"updrs_24r","total":10679,"1":1911,"2":4890,"3":3019,"4":755,"5":104},{"measure":"updrs_39","total":10114,"1":5581,"2":3464,"3":791,"4":182,"5":96}],
      width: 500,
      height: 500,
      svg: undefined,
      margin: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 50
      },
    };
  },
  computed: {
    translate() {
      return `translate(${this.margin.left}, ${this.margin.top})`;
    },
    // min() {
    //   return d3.min(this.dataset);
    // },
    // max() {
    //   return d3.max(this.dataset);
    // },
    // domain() {
    //   // return [this.min, this.max];
    //   return d3.extent(this.dataset); // [min, max]
    // },
    range() {
      return [0, this.height];
    },
    scale() {
      return d3
        .scaleLinear()
        .domain(this.domain)
        .range(this.range)
        .nice() // rounds domain to nice numbers
    },
    h() {
      return (
        this.height
        - this.margin.top
        - this.margin.bottom
      );
    },
    w() {
      return (
        this.width
        - this.margin.left
        - this.margin.right
      );
    },
    xScale() {
      return d3
        .scaleBand()
        .rangeRound([0, this.w])
        .padding(0.1)
        .align(0.1);
    },
    yScale() {
      return d3
        .scaleLinear()
        .rangeRound([this.h, 0]);
    },
    colorScale() {
      return d3
        .scaleOrdinal(d3.schemeAccent);
    },
    stack() {
      return d3
        .stack()
        .offset(d3.stackOffsetExpand);
    },
  },
  methods: {
    drawChart() {
      let outcomeMeasures = this
        .testData
        .map(d => d.measure);

      let cKeys = ['1','2','3','4','5'];

      this.xScale.domain(outcomeMeasures);
      this.colorScale(['1','2','3','4','5'])

      const serie = this
        .svg
        .selectAll(".serie")
        .data(this.stack.keys(cKeys)(this.testData))
        .enter().append("g")
          .attr("class", "serie")
          .attr("fill", d => this.colorScale(d.key));

      serie
        .selectAll("rect")
        .data(d => d)
        .enter().append("rect")
          .attr("x", d => this.xScale(d.data.measure))
          .attr("y", d => this.yScale(d[1]))
          .attr("height", d => this.yScale(d[0]) - this.yScale(d[1]))
          .attr("width", this.xScale.bandwidth());
    },
    drawAxis() {
      this
        .svg
        .append("g")
        .attr("class", "axis axis--x")
        .attr("transform", "translate(0," + this.h + ")")
        .call(d3.axisBottom(this.xScale));

      this
        .svg
        .append("g")
        .attr("class", "axis axis--y")
        .call(d3.axisLeft(this.yScale).ticks(10, "%"));
    },
    drawLegend() {
      const legend = this
        .svg
        .selectAll(".serie")
        .append("g")
        .attr("class", "legend")
        .attr("transform", d => {
          d = d[d.length - 1];
          return `translate(${this.xScale(d.data.measure)
            + this.xScale.bandwidth()}, ${(this.yScale(d[0]) + this.yScale(d[1]) / 2)}`;
        });

      legend.append("line")
        .attr("x1", -6)
        .attr("x2", 6)
        .attr("stroke", "#000");

      legend.append("text")
        .attr("x", 9)
        .attr("dy", "0.35em")
        .attr("fill", "#000")
        .style("font", "10px sans-serif")
        .text(d => d.key);
    },
  },
  mounted() {
    this.svg = d3.select(this.$el);
    this.drawChart();
    // this.drawAxis();
    // this.drawLegend();
  },
};
</script>
<style>
</style>