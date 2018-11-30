<template lang="pug">
  svg(
    @click='changeData(); updateData()'
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
      dataset: [5,10,15,20,25, 6, 23, 6],
      data: [{
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "2"
}, {
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "3"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "4"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_2",
  "score": "3"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "4"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "3"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "3"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "4"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "3"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "3"
}, {
  "measure": "updrs_2",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "2"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_24r",
  "score": "4"
}, {
  "measure": "updrs_24r",
  "score": "3"
}, {
  "measure": "updrs_20f",
  "score": "2"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_17",
  "score": "4"
}, {
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_24r",
  "score": "3"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "1"
}, {
  "measure": "updrs_24r",
  "score": "2"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_39",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "3"
}, {
  "measure": "updrs_39",
  "score": "2"
}, {
  "measure": "updrs_17",
  "score": "1"
}, {
  "measure": "updrs_2",
  "score": "1"
}, {
  "measure": "updrs_20f",
  "score": "3"
}],
      width: 500,
      height: 500,
      svg: undefined,
      margin: {
        top: 0,
        right: 0,
        bottom: 0,
        left: 0
      },
    };
  },
  computed: {
    translate() {
      return `translate(${this.margin.left}, ${this.margin.top})`;
    },
    min() {
      return d3.min(this.dataset);
    },
    max() {
      return d3.max(this.dataset);
    },
    domain() {
      // return Array(this.min, this.max);
      return d3.extent(this.dataset); // [min, max]
    },
    range() {
      return Array(0, this.height);
    },
    scale() {
      return d3
        .scaleLinear()
        .domain(this.domain)
        .range(this.range)
        .nice() // rounds domain to nice numbers
    },
    band() {
      // TODO
      // Use d3.scaleBand() to create scale for categorical bands
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
  },
  methods: {
    changeData() {
      this.dataset = this.dataset.map(d => Math.floor(Math.random() * 10));

      let foo = d3.range(3).map(() => Math.floor(Math.random() * 10));
      this.dataset = [...this.dataset, ...foo];
    },
    updateData() {
      const bars = this.svg.selectAll('rect').data(this.dataset)

      bars.exit().remove();

      bars.enter()
        .append('rect')
        .merge(bars)
        .attr('x', (d, i) => i * (this.w / this.dataset.length))
        .attr('width', this.w / this.dataset.length - 1)
        .transition()
        .ease(d3.easeCubicInOut)
        .attr('y', d => this.h - this.scale(d))
        .attr('height', d => this.scale(d))
        .attr('fill', d => `rgb(0, 0, ${Math.round(d * 10)})`);
    }
  },
  mounted() {
    this.svg = d3.select(this.$el);
    let foo = d3.map(this.data, d => d.measure).keys();
    let x = d3.scaleBand().domain(foo);
    const bars = this.svg
      .selectAll('rect')
      .data(this.dataset)

    bars
      .enter()
      .append('rect')
      .attr('x', (d, i) => i * (this.w / this.dataset.length))
      .attr('y', d => this.h - this.scale(d))
      .attr('width', this.w / this.dataset.length - 1)
      .attr('height', d => this.scale(d))
      .attr('fill', d => `rgb(0, 0, ${Math.round(d * 10)})`);
  },
};
</script>
<style>
</style>