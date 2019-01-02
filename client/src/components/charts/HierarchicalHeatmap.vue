<script>
/**
 * TODO:
 *  Make responsive to window resizing.
 */
import { select } from 'd3-selection';
import { nest } from 'd3-collection';
import { axisTop, axisLeft } from 'd3-axis';
import { scaleBand, scaleLinear } from 'd3-scale';
// import { schemeGreys } from 'd3-scale-chromatic';
import { max } from 'd3-array';

const Axes = {
  name: 'Axes',
  // eslint-disable-next-line no-unused-vars
  render(h) {
    return (
      <g>
        <g ref="xAxis" />
        <g ref="yAxis" />;
      </g>
    );
  },
  props: {
    scope: {
      required: true,
    },
    xScale: {
      type: Function,
      required: true,
    },
    yScale: {
      type: Function,
      required: true,
    },
  },
  data() {
    return {
      key: this.scope,
    };
  },
  computed: {
    xAxis() {
      return axisTop(this.xScale)
        .tickSize(0)
        .tickPadding(10);
    },
    yAxis() {
      return axisLeft(this.yScale)
        .tickSize(0)
        .tickPadding(10);
    },
  },
  methods: {
    drawAxes() {
      // Axes are complicated, so we let D3 handle this...
      select(this.$refs.xAxis)
        .call(this.xAxis)
        // For aesthetic reasons, lets remove the line
        .call(g => g.select('.domain').remove());
      select(this.$refs.yAxis)
        .call(this.yAxis)
        // For aesthetic reasons, lets remove the line
        .call(g => g.select('.domain').remove());
    },
  },
  watch: {
    scope() {
      // If column has been zoomed in on, we need to
      // update the axes.
      this.drawAxes();
    },
    xAxis() {
      this.drawAxes();
    },
    yAxis() {
      this.drawAxes();
    },
  },
  mounted() {
    this.drawAxes();
  },
};

const Grid = {
  name: 'Grid',
  // eslint-disable-next-line no-unused-vars
  render(h) {
    return (
      <g>
        {this.gridColumns.map(colData => (
          <GridColumn
            on-gridColClick={data => this.$emit('zoomIn', data)}
            on-gridColEnter={data => (this.active = data)}
            on-gridColLeave={() => (this.active = null)}
            isActive={!this.active || this.active === colData.key}
            data={colData}
            xScale={this.xScale}
            yScale={this.yScale}
            colorScale={this.colorScale}
            tileHeight={this.tileHeight}
            tileWidth={this.tileWidth}
          />
        ))}
      </g>
    );
  },
  data() {
    return {
      active: null,
    };
  },
  props: {
    data: {
      type: Array,
      required: true,
    },
    xScale: {
      type: Function,
      required: true,
    },
    yScale: {
      type: Function,
      required: true,
    },
    colorScale: {
      type: Function,
      required: true,
    },
    tileHeight: {
      type: Number,
      required: true,
    },
    tileWidth: {
      type: Number,
      required: true,
    },
  },
  computed: {
    gridColumns() {
      return nest()
        .key(d => d.name) // TODO: Make this a prop
        .entries(this.data);
    },
  },
  methods: {
    zoomIntoColumn(data) {
      this.data = [
        {
          name: 'Foo',
          dataset: 'PPMI',
          measures: 3,
        },
        {
          name: 'Bar',
          dataset: 'HOME',
          measures: 1,
        },
        {
          name: 'Quz',
          dataset: 'PPMI',
          measures: 2,
        },
        {
          name: 'Quz',
          dataset: 'HOME',
          measures: 4,
        },
      ];
    },
  },
};
const GridColumn = {
  name: 'GridColumn',
  // eslint-disable-next-line no-unused-vars
  render(h) {
    return (
      <g
        onClick={() => this.$emit('gridColClick', this.data.key)}
        onMouseenter={() => this.$emit('gridColEnter', this.data.key)}
        onMouseleave={() => this.$emit('gridColLeave', this.data.key)}
        class={this.isActive ? 'active' : 'dim'}
      >
        {this.data.values.map(d => (
          <GridTile
            x={this.xScale(d.name)}
            y={this.yScale(d.dataset)}
            fill={this.colorScale(d.outcomeMeasures.length)}
            width={this.tileWidth}
            height={this.tileHeight}
          />
        ))}
      </g>
    );
  },
  props: {
    isActive: {
      type: Boolean,
      required: true,
    },
    data: {
      type: Object,
      required: true,
    },
    xScale: {
      type: Function,
      required: true,
    },
    yScale: {
      type: Function,
      required: true,
    },
    colorScale: {
      type: Function,
      required: true,
    },
    tileWidth: {
      type: Number,
      required: true,
    },
    tileHeight: {
      type: Number,
      required: true,
    },
  },
};

const GridTile = {
  name: 'GridTile',
  // eslint-disable-next-line no-unused-vars
  render(h) {
    return (
      <rect
        class="tile"
        x={this.x}
        y={this.y}
        fill={this.fill}
        width={this.width}
        height={this.height}
      />
    );
  },
  props: {
    x: {
      type: Number,
      required: true,
    },
    y: {
      type: Number,
      required: true,
    },
    fill: {
      type: String,
      required: true,
    },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
    },
  },
};

export default {
  props: {
    data: {
      type: Array,
      required: true,
    },
    layout: {
      type: Object,
      default: () => ({
        width: 1200,
        height: 250,
        margin: {
          top: 50,
          right: 50,
          bottom: 50,
          left: 50,
        },
      }),
    },
  },
  data() {
    return {
      // Initially clone property. This will be updated
      // as user interacts with the grid an zoom into
      // a particular child of the heatmap.
      scopedData: [...this.data],
      zoomed: false,
      scope: null,
      outerWidth: this.layout.width,
      outerHeight: this.layout.height,
    };
  },
  computed: {
    translateMargin() {
      const { left, top } = this.layout.margin;
      return `translate(${left},${top})`;
    },
    height() {
      const { top, bottom } = this.layout.margin;
      return this.outerHeight - top - bottom;
    },
    width() {
      const { left, right } = this.layout.margin;
      return this.outerWidth - left - right;
    },
    categories() {
      return [...new Set(this.scopedData.map(d => d.name))];
    },
    datasets() {
      return [...new Set(this.scopedData.map(d => d.dataset))];
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
        .range([this.height, 0]);
    },
    colorScale() {
      return scaleLinear()
        .domain([0, max(this.scopedData, d => d.outcomeMeasures.length)])
        .range(['white', '#2196F3']);
    },
  },
  mounted() {
    this.$nextTick(() => {
      const { height, width } = this.$el.getBoundingClientRect();
      this.outerWidth = width;
      this.outerHeight = height;
    });
  },
  methods: {
    zoomInHandler(data) {
      const gridCol = this.data.filter(d => d.name === data);
      const outcomeMeasures = gridCol.map(dataset => ({
        dataset: dataset.dataset,
        name: dataset.name,
        outcomeMeasures: dataset.outcomeMeasures.map(m => ({
          ...m,
          outcomeMeasures: [1],
        })),
      }));
      const newScopedData = outcomeMeasures.reduce(
        (acc, { outcomeMeasures: curr }) => [...acc, ...curr],
        []
      );
      this.scope = data;
      this.scopedData = newScopedData;
    },
  },
  // eslint-disable-next-line no-unused-vars
  render(h) {
    // const { width, height } = this.layout;
    // const viewBox = `0 0 ${width} ${height}`;
    return (
      <div>
        <svg ref="chart" width={this.layout.width} height={this.layout.height}>
          <g transform={this.translateMargin}>
            <Axes
              xScale={this.xScale}
              yScale={this.yScale}
              scope={this.scope}
            />
            <Grid
              on-zoomIn={this.zoomInHandler}
              data={this.scopedData}
              xScale={this.xScale}
              yScale={this.yScale}
              colorScale={this.colorScale}
              tileHeight={this.tileHeight}
              tileWidth={this.tileWidth}
            />
          </g>
        </svg>
      </div>
    );
  },
};
</script>

<style>
rect.tile {
  stroke: white;
  stroke-width: 3px;
  stroke-opacity: 0.6;
}

.dim {
  opacity: 0.25;
  transition: opacity 0.25s ease-in-out;
  -moz-transition: opacity 0.25s ease-in-out;
  -webkit-transition: opacity 0.25s ease-in-out;
}
.active {
  cursor: pointer;
  opacity: 1;
  transition: opacity 0.25s ease-in-out;
  -moz-transition: opacity 0.25s ease-in-out;
  -webkit-transition: opacity 0.25s ease-in-out;
}
</style>
