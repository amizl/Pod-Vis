<template>
  <svg
    :width='layout.width'
    :height='layout.height'
  >
    <g
    :transform='transform'
    >
      <!-- X AXIS -->
      <g class='axis' ref='xAxis'></g>
      <!-- Y AXIS -->
      <g class='axis' ref='yAxis'></g>
      <!-- HEATMAP COLUMNS -->
      <g
        v-for='tileColumn in tileColumns'
        :key='tileColumn.key'
        @mouseover='mouseoverColumn'
      >
      <!-- HEATMAP TILES -->
        <rect
          v-for='tile in tileColumn.tiles'
          :x='tile.x'
          :y='tile.y'
          :fill='tile.fill'
          :width='tileWidth'
          :height='tileHeight'
          class='tile'
          :key='tile.key'
        >
        </rect>
      </g>
    </g>
  </svg>
</template>

<script>
import { select } from 'd3-selection';
import { nest } from 'd3-collection';
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
    // options: {
    //   type: Object
    // },
    layout: {
      type: Object,
      default: () => {
        return {
          width: 1000,
          height: 300,
          margin: {
            top: 50,
            right: 50,
            bottom: 50,
            left: 50,
          }
        };
      },
    },
  },
  data () {
    return {
      colorRange: ['white', 'steelblue'],
      hovered: null,
    };
  },
  computed: {
    tileColumns() {
      const columns = nest()
        .key(d => d.category)
        .entries(this.data);

      return columns.map(column => {
        return {
          active: this.columnKeyhovered,
          key: column.key,
          tiles:  column.values.map(d => {
            return {
              key: d.category + "," + d.dataset,
              x: this.xScale(d.category),
              y: this.yScale(d.dataset),
              fill: this.colorScale(d.measures)
            };
          })
        };
      });
    },
    height() {
      const { height } = this.layout;
      const { top, bottom } = this.layout.margin;
      return height - top - bottom;
    },
    width() {
      const { width } = this.layout;
      const { left, right } = this.layout.margin;
      return width - left - right;
    },
    transform() {
      const { left, top } = this.layout.margin;
      return "translate(" + left + "," + top + ")";
    },
    categories() {
      return [...new Set(this.data.map(d => d.category))];
    },
    datasets () {
      return [...new Set(this.data.map(d => d.dataset))];
    },
    tileWidth() {
      return Math.floor(this.width / this.categories.length);
    },
    tileHeight() {
      return Math.floor(this.height / this.datasets.length);
    },
    xScale() {
      return scaleBand()
        .domain(this.categories)
        .range([0, this.width]);
    },
    yScale() {
      return scaleBand()
        .domain(this.datasets)
        .range([this.height, 0])
    },
    colorScale() {
      return scaleLinear()
        .domain([0, max(this.data, d => d.measures)])
        .range(this.colorRange)
    },
    xAxis() {
      return axisTop(this.xScale)
        // .tickSizeOuter(0)
        .tickSize(0)
        .tickPadding(10);
    },
    yAxis() {
      return axisLeft(this.yScale)
        // .tickSizeOuter(0)
        .tickSize(0)
        .tickPadding(10);
    },
  },
  methods: {
    mouseoverColumn({ target }) {
      console.log(target.parentElement);
    }
  },
  mounted() {
    // Axis are complicated, so we let D3 handle this...
    select(this.$refs.xAxis)
      .call(this.xAxis)
      // For aesthetic reasons, lets remove the line
      .call(g => g.select(".domain").remove())

    select(this.$refs.yAxis)
      .call(this.yAxis)
      // For aesthetic reasons, lets remove the line
      .call(g => g.select(".domain").remove());
  },
};
</script>

<style scoped>
rect.tile {
  stroke: white;
  stroke-width: 3px;
  stroke-opacity: .6;
}

text.label {
  text-anchor: middle;
}

g.axis > path.domain {
  fill: none;
  stroke: white;
  shape-rendering: crispEdges;
}
</style>
