<template>
  <svg>
  </svg>
</template>

<script>
import { select } from 'd3-selection';
import { axisTop, axisLeft } from 'd3-axis';
import { scaleBand, scaleLinear, scaleOrdinal, } from 'd3-scale';
import { stack, stackOffsetExpand } from 'd3-shape';
import { schemeGreys } from 'd3-scale-chromatic';
import { max } from 'd3-array';

export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      width: 1000, // Should be prop
      height: 500, // Should be prop
      margin: {
        top: 50,
        right: 50,
        bottom: 50,
        left: 50,
      },
    }
  },
  mounted() {
    const width = this.width
      - this.margin.left
      - this.margin.right;
    const height = this.height
      - this.margin.top
      - this.margin.bottom;

    const svg = select(this.$el)
      .attr("width", this.width)
      .attr("height", this.height)
      .append("g")
      .attr("transform", "translate(" + this.margin.left + "," + this.margin.top + ")")
      .attr('height', height)
      .attr('width', width);
    const categorys = [
      ...new Set(this.data.map(d => d.category))
    ];
    const datasets = [
      ...new Set(this.data.map(d => d.dataset))
    ]

    const xGridSize = Math.floor(width / categorys.length);
    const yGridSize = Math.floor(height / datasets.length);

    const xScale = scaleBand()
      .domain(categorys)
      .range([0, width]);

    const yScale = scaleBand()
      .domain(datasets)
      .range([height, 0]);

    const zScale = scaleLinear()
      .domain([0, max(this.data, d => d.measures)])
      .range(["white", "steelblue"]);

    const xAxis = axisTop(xScale);
    const yAxis = axisLeft(yScale);

    svg
      .append('g')
      .call(xAxis);
    svg
      .append('g')
      .call(yAxis);

    svg.selectAll(".tile")
      .data(this.data)
      .enter()
      .append("rect")
      .attr("class", "tile")
      .attr("x", d => xScale(d.category))
      .attr("y", d => yScale(d.dataset))
      .attr("width", xGridSize)
      .attr("height",  yGridSize)
      .style("fill", d => zScale(d.measures));
  },
};
</script>

<style scoped>

</style>
