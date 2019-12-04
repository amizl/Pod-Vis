<script>
import { select } from 'd3-selection';
import { axisTop, axisLeft } from 'd3-axis';
import { scaleBand, scaleLinear, scaleOrdinal } from 'd3-scale';
import { stack, stackOffsetExpand } from 'd3-shape';
import { schemeGreys } from 'd3-scale-chromatic';

// X and Y axes component
const Axes = {
  props: {
    height: Number,
    xScale: Function,
    yScale: Function,
  },
  computed: {
    axisX() {
      return axisTop()
        .scale(this.xScale)
        .ticks(10, '%');
    },
    axisY() {
      return axisLeft().scale(this.yScale);
    },
  },
  render() {
    // eslint-disable-line no-unused-vars
    const axisX = <g ref="axisX" />; // transform={`translate(0, ${this.height})`}/>;
    // const axisY = <g ref='axisY'/>;
    return <g>{axisX}</g>;
  },
  mounted() {
    // Vue no longer allows callbacks inside ref property.
    // If it did, we would have <g ref={ (node) => select(node).call(...)/>,
    // inside of the render function. So instead, we take advantage
    // of the mounted life cycle hook to reference the X and
    // Y axes and use d3's select and call to actually draw
    // the axes/ticks in the svg. It's a little hacky because here
    // d3 is actually still doing DOM manipulation, which we want
    // to avoid. But I am unaware of a better way at this moment
    // to draw axes/ticks inside Vue.
    const { axisX } = this.$refs;
    const { axisY } = this.$refs;

    select(axisX).call(this.axisX);
    select(axisY).call(this.axisY);
  },
};

const Legend = {
  props: {
    colorScale: Function,
    labels: Array,
  },
  computed: {
    scale() {
      return scaleBand()
        .rangeRound([0, 500])
        .padding(0.05)
        .align(0.1)
        .domain(this.labels);
    },
  },
  render() {
    // eslint-disable-line no-unused-vars
    return (
      <g>
        {this.labels.map(label => (
          <g transform={`translate(${this.scale(label.toString())}, 0)`}>
            <rect
              x="0"
              y="0"
              width="10"
              height="10"
              fill={this.colorScale(label)}
            />
            <text x="20" y="10" fill="black">
              {label}
            </text>
          </g>
        ))}
      </g>
    );
  },
};
// const Legend = {
//   // TODO
//   methods: {
//     drawLegend() {
//       const legend = this
//         .svg
//         .selectAll(".serie")
//         .append("g")
//         .attr("class", "legend")
//         .attr("transform", d => {
//           d = d[d.length - 1];
//           return `translate(${this.xScale(d.data.measure)
//             + this.xScale.bandwidth()}, ${(this.yScale(d[0]) + this.yScale(d[1]) / 2)}`;
//         });

//       legend.append("line")
//         .attr("x1", -6)
//         .attr("x2", 6)
//         .attr("stroke", "#000");

//       legend.append("text")
//         .attr("x", 9)
//         .attr("dy", "0.35em")
//         .attr("fill", "#000")
//         .style("font", "10px sans-serif")
//         .text(d => d.key);
//     },
//   }
// };

export default {
  props: {
    data: {
      type: Array,
      default: () => [],
    },
  },
  data() {
    return {
      testData: [
        {
          measure: 'updrs_17',
          total: 4901,
          '1': 3351,
          '2': 848,
          '3': 478,
          '4': 202,
          '5': 22,
        },
        {
          measure: 'updrs_2',
          total: 10158,
          '1': 7189,
          '2': 1779,
          '3': 842,
          '4': 307,
          '5': 41,
        },
        {
          measure: 'updrs_20f',
          total: 10603,
          '1': 9494,
          '2': 677,
          '3': 366,
          '4': 59,
          '5': 7,
        },
        {
          measure: 'updrs_24r',
          total: 10679,
          '1': 1911,
          '2': 4890,
          '3': 3019,
          '4': 755,
          '5': 104,
        },
        {
          measure: 'updrs_39',
          total: 10114,
          '1': 5581,
          '2': 3464,
          '3': 791,
          '4': 182,
          '5': 96,
        },
      ],
      rawWidth: 500, // Should be prop
      rawHeight: 150, // Should be prop
      margin: {
        top: 50,
        right: 25,
        bottom: 20,
        left: 25,
      },
    };
  },
  computed: {
    translate() {
      return `translate(${this.margin.left}, ${this.margin.top})`;
    },
    height() {
      return this.rawHeight - this.margin.top - this.margin.bottom;
    },
    width() {
      return this.rawWidth - this.margin.left - this.margin.right;
    },
    domain() {
      return this.data.map(d => d.cohort);
    },
    yScale() {
      return scaleBand()
        .rangeRound([0, this.height])
        .padding(0.05)
        .align(0.1)
        .domain(this.domain);
    },
    xScale() {
      return scaleLinear().rangeRound([0, this.width]);
    },
    colorScale() {
      return scaleOrdinal(schemeGreys[6]).domain([0, 1, 2, 3, 4, 5]); // TODO: need better way than to hardcode domain
    },
    stack() {
      return stack()
        .offset(stackOffsetExpand)
        .keys([1, 2, 3, 4, 5]);
    },
  },
  methods: {},
  render() {
    // eslint-disable-line no-unused-vars
    const bars = this.stack(this.data).map(cohort => (
      <g fill={this.colorScale(cohort.key)}>
        {cohort.map(score => (
          <rect
            x={this.xScale(score[0])}
            y={this.yScale(score.data.cohort)}
            height={this.yScale.bandwidth()}
            width={this.xScale(score[1]) - this.xScale(score[0])}
          />
        ))}
      </g>
    ));

    return (
      <svg width={this.rawWidth} height={this.rawHeight}>
        <g transform={`translate(${this.margin.left}, 10)`}>
          <Legend colorScale={this.colorScale} labels={[1, 2, 3, 4, 5]} />
        </g>
        <g transform={this.translate}>
          <Axes
            height={this.height}
            xScale={this.xScale}
            yScale={this.yScale}
          />
          {bars}
        </g>
      </svg>
    );
  },
};
</script>
<style></style>
