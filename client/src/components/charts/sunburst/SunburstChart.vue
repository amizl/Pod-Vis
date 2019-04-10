<template>
  <v-layout class="graph">
    <v-flex xs6>
      <v-flex xs2>
        <p class="mb-0 display-1 font-weight-bold text-xs-right">
          {{ ((100 * current.value) / root.value) | toPrecision3 }}%
        </p>
        <p class="caption text-xs-right">
          {{ current.value }}/{{ root.value }}
        </p>
      </v-flex>
      <div id="chart"></div>
    </v-flex>
    <v-flex xs6>
      <slot
        :data="data"
        :color="color"
        :actions="actions"
        :nodes="nodes"
        name="legend"
      ></slot>
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
import {
  hierarchy as d3Hierarchy,
  partition as d3Partition,
} from 'd3-hierarchy';
import { arc as d3Arc } from 'd3-shape';
import { path as d3Path } from 'd3-path';
import { interpolate as d3Interpolate } from 'd3-interpolate';
import { transition as d3Transition } from 'd3-transition';
import { schemeCategory10 as d3SchemeCategory10 } from 'd3-scale-chromatic';
import { schemePaired as d3SchemePaired } from 'd3-scale-chromatic';
import { schemeSpectral as d3SchemeSpectral } from 'd3-scale-chromatic';
import { format as d3Format } from 'd3-format';

function getUniqueNodeId(node) {
  return node
    .ancestors()
    .map(node => node.data.name)
    .join('-');
}

/**
 * Join each entry and its key in data with '-'. We join the keys in a specific order
 * specified by keyOrder
 * {param} Array - Array of objects.
 * {param} Array - Array of keys in specific order to map data to.
 *
 * Returns 2-dimensonal array needed to build a hierarchy.
 */
function mapWithDash(data, keyOrder) {
  return data.map(d => {
    const values = keyOrder.map(key => d[key]);
    return [values.join('-'), d['count']];
  });
}

/**
 * Takes csv-like structure (two-dimensional array) and builds a hierarchical
 * structure needed to build sunburst chart.
 *
 * {param} Array - Two-dimensional array created by mapWithDash
 */
function buildHierarchy(csv) {
  let currentId = 0;
  const root = { id: currentId++, name: 'root', children: [] };
  for (let i = 0; i < csv.length; i++) {
    let sequence = csv[i][0];
    let size = +csv[i][1];
    if (isNaN(size)) {
      // e.g. if this is a header row
      continue;
    }
    let parts = sequence.split('-');
    let currentNode = root;
    for (var j = 0; j < parts.length; j++) {
      let children = currentNode['children'];
      let nodeName = parts[j];
      let childNode;
      if (j + 1 < parts.length) {
        // Not yet at the end of the sequence; move down the tree.
        let foundChild = false;
        for (var k = 0; k < children.length; k++) {
          if (children[k]['name'] == nodeName) {
            childNode = children[k];
            foundChild = true;
            break;
          }
        }
        // If we don't already have a child node for this branch, create it.
        if (!foundChild) {
          childNode = { id: currentId++, name: nodeName, children: [] };
          children.push(childNode);
        }
        currentNode = childNode;
      } else {
        // Reached the end of the sequence; create a leaf node.
        childNode = { id: currentId++, name: nodeName, size: size };
        children.push(childNode);
      }
    }
  }
  return root;
}

export default {
  components: {},
  filters: {
    toPrecision3(value) {
      if (value) {
        return value.toPrecision(3);
      }
    },
  },
  props: {
    data: Array,
    keyorder: Array,
  },
  data() {
    return {
      hierachicalData: {},
      width: 200,
      height: 200,
      svg: undefined,
      current: {},
    };
  },
  computed: {
    partition() {
      return d3Partition();
    },
    root() {
      return d3Hierarchy(this.data)
        .sum(d => d.size)
        .sort((a, b) => b.value - a.value);
    },
    nodes() {
      return this.partition(this.root)
        .descendants()
        .filter(node => node.data.name !== '');
    },
    radius() {
      return Math.min(this.width, this.height) / 2 - 10;
    },
    x() {
      return d3ScaleLinear().range([0, 2 * Math.PI]);
    },
    y() {
      return d3ScaleSqrt().range([0, this.radius]);
    },
    arc() {
      return d3Arc()
        .startAngle(d => Math.max(0, Math.min(2 * Math.PI, this.x(d.x0))))
        .endAngle(d => Math.max(0, Math.min(2 * Math.PI, this.x(d.x1))))
        .innerRadius(d => Math.max(0, this.y(d.y0)))
        .outerRadius(d => Math.max(0, this.y(d.y1)));
    },
    colorDomain() {
      const nodeNames = this.nodes
        .map(({ data }) => data.name)
        .filter(el => el !== '');
      return [...new Set(nodeNames)];
    },
    color() {
      let color = d3ScaleOrdinal(d3SchemeCategory10).domain(this.colorDomain);
      // .range([
      //         "#5254a3",
      //         "#6b6ecf",
      //         "#9c9ede",
      //         "#637939",
      //         "#8ca252",
      //         "#b5cf6b",
      //         "#cedb9c",
      //         "#8c6d31",
      //         "#bd9e39",
      //         "#e7ba52",
      //         "#e7cb94",
      //         "#843c39",
      //         "#ad494a",
      //         "#d6616b",
      //         "#e7969c",
      //         "#7b4173",
      //         "#a55194",
      //         "#ce6dbd",
      //         "#de9ed6"]);
      return color;
    },
    actions() {
      return {
        zoomToNode: this.zoomToNode.bind(this),
        highlightPath: this.highlightPath.bind(this),
        updateCurrent: this.updateCurrent.bind(this),
      };
    },
  },
  mounted() {
    let width = this.width,
      height = this.height,
      radius = this.radius,
      x = this.x,
      y = this.y,
      partition = this.partition,
      arc = this.arc,
      root = this.root,
      nodes = this.nodes,
      formatNumber = d3Format(',d');

    let svg = d3Select('#chart')
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .append('g')
      .attr('transform', 'translate(' + width / 2 + ',' + height / 2 + ')');
    this.svg = svg;

    let color = this.color;
    this.current = this.root;

    const foo = svg
      .selectAll('path')
      .data(nodes, getUniqueNodeId)
      .enter()
      .append('path')
      // the display attribute of the <path> element for our root node to "none".
      // (display="none" tells SVG that this element will not be rendered.)
      .attr('display', d => (d.depth ? null : 'none'))
      // fills in all the "d" attributes of each <path>
      // element with the values from our arc variable
      .attr('d', arc)
      // with a fill-rule of evenodd, the inside/outside state changes
      // every time you cross a path edge
      .attr('fill-rule', 'evenodd')
      // add a stroke to each path
      .style('stroke', '#fff')
      .style('opacity', d => {
        const childrenIds = this.current.children.map(node => node.data.id);

        if (childrenIds.includes(d.data.id)) {
          return 1;
        } else {
          return 0.2;
        }
      })
      .style('fill', function(d) {
        // return color((d.children ? d : d.parent).data.name);
        return color(d.data.name);
      });

    // .on("click", this.click)
    // .on('mouseover', (d) => console.log(d))
    // .append("title")
    // .text(function(d) { return d.data.name + "\n" + formatNumber(d.value); });
  },
  created() {
    const formattedData = mapWithDash(this.data, this.keyorder);
    this.data = buildHierarchy(formattedData);
  },
  methods: {
    updateCurrent(node) {
      this.current = node;
    },
    getNodeById(id) {
      if (id === undefined) id = 1;

      const path = this.pathes
        .nodes()
        .find(({ __data__: data }) => data.data.id == id);
      if (path) {
        return path.__data__;
      } else {
        return null;
      }
    },
    highlightPath(node, opacity = 0.3) {
      const sequenceArray = node.ancestors();
      this.svg
        .selectAll('path')
        .filter(d => sequenceArray.indexOf(d) === -1)
        .transition()
        .duration(750)
        .style('opacity', opacity);
      this.svg
        .selectAll('path')
        .filter(d => sequenceArray.indexOf(d) >= 0)
        .style('opacity', 1);
    },
    zoomToNode(node) {
      const t = d3Transition()
        .duration(750)
        .tween('scale', () => {
          const xd = d3Interpolate(this.x.domain(), [node.x0, node.x1]),
            yd = d3Interpolate(this.y.domain(), [node.y0, 1]),
            yr = d3Interpolate(this.y.range(), [node.y0 ? 20 : 0, this.radius]);
          return t => {
            this.x.domain(xd(t));
            this.y.domain(yd(t)).range(yr(t));
          };
        });

      // Because this zoomToNode is being passed to a slot component,
      // and being called inside the child, this.svg might not yet be
      // defined
      if (this.svg) {
        this.svg
          .selectAll('path')
          .transition(t)
          .attrTween('d', node => () => this.arc(node))
          .style('opacity', node => {
            // If node is current node, let's keep its opacity at 1,
            // that way we can easily visualize the parent ring
            if (this.current.data.id === node.data.id) return 1;
            // Keep leaf nodes' opacity at 1
            if (!this.current.children) return 1;

            const childrenIds = this.current.children.map(node => node.data.id);

            if (childrenIds.includes(node.data.id)) {
              return 1;
            } else {
              return 0.2;
            }
          });
      }
    },
  },
  getPathes() {
    return this.svg.selectAll('path').data(this.nodes, getUniqueNodeId);
  },
};
</script>

<style scoped></style>
