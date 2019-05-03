<template lang="pug">
  svg(
    :width='width'
    :height='height'
  )
    g(:transform='translate')
      //- paths will be updated by d3 here...
</template>

<script>
import * as d3 from 'd3';

export default {
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      width: 250,
      height: 250,
      g: undefined,
    };
  },
  computed: {
    radius() {
      return Math.min(this.width, this.height) / 2;
    },
    translate() {
      return `translate(${this.width / 2}, ${this.height / 2})`;
    },
  },
  watch: {
    data() {
      this.update();
    },
  },
  mounted() {
    this.g = d3.select(this.$el.firstChild);
    this.drawChart();
  },
  methods: {
    update() {
      const color = d3
        .scaleOrdinal(d3.schemeCategory10)
        .domain(this.data.map(d => d.code));

      const pie = d3
        .pie()
        .value(d => d.n_samples)
        .sort(null);

      const arc = d3
        .arc()
        .innerRadius(this.radius - 30)
        .outerRadius(this.radius - 5);

      const arcs = this.g.selectAll('g').data(pie(this.data));

      arcs.exit().remove();

      arcs
        .enter()
        .append('g')
        .append('path')
        .attr('fill', d => color(d.code))
        .attr('d', arc)
        .each(function(d) {
          this._current = d;
        });

      const totalSamples = this.data
        .map(d => d.n_samples)
        .reduce((acc, curr) => acc + curr);

      this.g
        .select('text')
        .attr('text-anchor', 'middle')
        .attr('y', 0)
        .text(`${totalSamples} Samples Selected`);
    },
    drawChart() {
      const color = d3
        .scaleOrdinal(d3.schemeCategory10)
        .domain(this.data.map(d => d.code));

      const pie = d3
        .pie()
        .value(d => d.n_samples)
        .sort(null);
      const arc = d3
        .arc()
        .innerRadius(this.radius - 30)
        .outerRadius(this.radius - 5);

      this.g
        .selectAll('g')
        .data(pie(this.data))
        .enter()
        .append('g')
        .append('path')
        .attr('fill', d => color(d.code))
        .attr('d', arc)
        .each(function(d) {
          this._current = d;
        });

      const totalSamples = this.data
        .map(d => d.n_samples)
        .reduce((acc, curr) => acc + curr);

      this.g
        .append('text')
        .attr('text-anchor', 'middle')
        .attr('y', 0)
        .text(`${totalSamples} Samples Selected`);
    },
  },
};
</script>
<style></style>
