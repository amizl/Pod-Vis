<template>
  <v-layout class="graph">
    <v-flex xs6>
      <slot name="legend"></slot>
    </v-flex>
    <v-flex xs6>
      <div id='chart'></div>
    </v-flex>
  </v-layout>
</template>

<script>
import { select as d3Select, event as d3Event } from 'd3-selection';
import {
  scaleLinear as d3ScaleLinear,
  scaleSqrt as d3ScaleSqrt,
  scaleOrdinal as d3ScaleOrdinal,
} from 'd3-scale';
import { hierarchy as d3Hierarchy, partition as d3Partition } from 'd3-hierarchy';
import { arc as d3Arc } from 'd3-shape';
import { path as d3Path } from 'd3-path';
import { interpolate as d3Interpolate } from 'd3-interpolate';
import { transition as d3Transition } from 'd3-transition';
import { schemeCategory10 as d3SchemeCategory10 } from 'd3-scale-chromatic';
import { schemeSpectral as d3SchemeSpectral } from 'd3-scale-chromatic';
import { format as d3Format } from 'd3-format';

export default {
  props: {
    data: Object,
  },
  components: {

  },
  mounted() {
    // console.log(d3SchemeSpectral);
    let width = 200,
        height = 200,
        radius = (Math.min(width, height) / 2) - 10;
    let formatNumber = d3Format(",d");
    let x = d3ScaleLinear()
      .range([0, 2 * Math.PI]);
    let y = d3ScaleSqrt()
      .range([0, radius]);

    let partition = d3Partition();

    let arc = d3Arc()
      .startAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x0))); })
      .endAngle(function(d) { return Math.max(0, Math.min(2 * Math.PI, x(d.x1))); })
      .innerRadius(function(d) { return Math.max(0, y(d.y0)); })
      .outerRadius(function(d) { return Math.max(0, y(d.y1)); });

    let svg = d3Select("#chart").append("svg")
        .attr("width", width)
        .attr("height", height)
      .append("g")
        .attr("transform", "translate(" + width / 2 + "," + (height / 2) + ")");
    console.log(this.data);

    const root = d3Hierarchy(this.data);
    const nodes = partition(root).descendants();

    const nodeNames = nodes
      .map(({ data }) => data.name)
      .filter(el => el !== 'root' && el !== '');

    const colorDomain = [...new Set(nodeNames)];

    console.log(colorDomain);
    let color = d3ScaleOrdinal() // (d3SchemeCategory10)
      .domain(colorDomain)
      .range(["#393b79",
              "#5254a3",
              "#6b6ecf",
              "#9c9ede",
              "#637939",
              "#8ca252",
              "#b5cf6b",
              "#cedb9c",
              "#8c6d31",
              "#bd9e39",
              "#e7ba52",
              "#e7cb94",
              "#843c39",
              "#ad494a",
              "#d6616b",
              "#e7969c",
              "#7b4173",
              "#a55194",
              "#ce6dbd",
              "#de9ed6"]);

    root.sum(function(d) { return d.size; });
    console.log(partition(root).descendants());
    const children = partition(root)
      .descendants()
      .filter(node => node.data.name !== '')

    svg.selectAll("path")
      .data(children)
      .enter().append("path")
      .attr("d", arc)
      .attr("fill-rule", "evenodd")
      .style("fill", function(d) {
        console.log(d.data.name);
        console.log(color(d.data.name));
        // return color((d.children ? d : d.parent).data.name);
        return color(d.data.name);
      })
      // .style("fill", function(d) { return this.colors[d.data.name]; })
      .on("click", click)
      .on('mouseover', ({data}) => console.log(data.name))
      .append("title")
      .text(function(d) { return d.data.name + "\n" + formatNumber(d.value); })

    function click(d) {
      d3Transition()
        .duration(750)
        .tween("scale", function() {
          var xd = d3Interpolate(x.domain(), [d.x0, d.x1]),
              yd = d3Interpolate(y.domain(), [d.y0, 1]),
              yr = d3Interpolate(y.range(), [d.y0 ? 20 : 0, radius]);
          return function(t) { x.domain(xd(t)); y.domain(yd(t)).range(yr(t)); };
        })
        .selectAll("path")
        .attrTween("d", function(d) { return function() { return arc(d); }; });
}
  },
}
</script>

<style scoped>

</style>