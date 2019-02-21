<template>
<v-card>
  <div id="sequence"></div>
  <div id="chart">
    <div id="explanation" style='visibility: hidden;'>
      <span id="percentage"></span> <br/>
    </div>
  </div>
</v-card>
</template>

<script>
import * as d3 from 'd3';
import { hierarchy, partition } from 'd3-hierarchy';
import { arc } from 'd3-shape';

export default {
  props: {
    data: Object,
  },
  data() {
    return {
      width: 750,
      height: 170,
      b: {
        w: 75,
        h: 30,
        s: 3,
        t: 10,
      },
    }
  },
  methods: {
    createVisualization(json) {
      // Basic setup of page elements.
      // this.initializeBreadcrumbTrail();
      // this.drawLegend();
      // d3.select("#togglelegend").on("click", this.toggleLegend);

      // Bounding circle underneath the sunburst, to make it easier to detect
      // when the mouse leaves the parent g.
      this.vis.append("svg:circle")
          .attr("r", this.radius)
          .style("opacity", 0);

      // Turn the data into a d3 hierarchy and calculate the sums.
      console.log(json);
      const root = d3.hierarchy(json)
          // .sum(function(d) { return d.size; })
          // .sort(function(a, b) { return b.value - a.value; });
      console.log(root);
      // For efficiency, filter nodes to keep only those large enough to see.
      const nodes = this.partition(root)// (root).descendants();
          // .filter(function(d) {
          //   // console.log(d);
          //     return (d.x1 - d.x0 > 0.005); // 0.005 radians = 0.29 degrees
          // });
      console.log('Nodes');
      console.log(nodes);

      const path = this.vis.data([json]).selectAll("path")
          .data(nodes)
          .enter().append("svg:path")
          .attr("display", function(d) { return d.depth ? null : "none"; })
          .attr("d", this.arc)
          // .attr("fill-rule", "evenodd")
          // .style("fill", function(d) { return this.colors[d.data.name]; })
          // .style("opacity", 1)
          // .on("mouseover", this.mouseover);

      console.log('foo');
      console.log(path);

      // Add the mouseleave handler to the bounding circle.
      // d3.select("#container").on("mouseleave", this.mouseleave);

      // Get total size of the tree = value of root node from partition.
      // this.totalSize = path.datum().value;
    },
    mouseover(d) {
      const percentage = (100 * d.value / this.totalSize).toPrecision(3);
      const percentageString = percentage + "%";
      if (percentage < 0.1) {
        percentageString = "< 0.1%";
      }

      d3.select("#percentage")
          .text(percentageString);

      d3.select("#explanation")
          .style("visibility", "");

      const sequenceArray = d.ancestors().reverse();
      sequenceArray.shift(); // remove root node from the array
      updateBreadcrumbs(sequenceArray, percentageString);

      // Fade all the segments.
      d3.selectAll("path")
          .style("opacity", 0.3);

      // Then highlight only those that are an ancestor of the current segment.
      this.vis.selectAll("path")
        .filter(function(node) {
          return (sequenceArray.indexOf(node) >= 0);
        })
        .style("opacity", 1);
    },
    mouseleave(d) {
      // Hide the breadcrumb trail
      d3.select("#trail")
        .style("visibility", "hidden");

      // Deactivate all segments during transition.
      d3.selectAll("path").on("mouseover", null);

      // Transition each segment to full opacity and then reactivate it.
      d3.selectAll("path")
        .transition()
        .duration(1000)
        .style("opacity", 1)
        .on("end", function() {
          d3.select(this).on("mouseover", this.mouseover);
        });
      d3.select("#explanation")
        .style("visibility", "hidden");
    },
    initializeBreadcrumbTrail() {
      // Add the svg area.
      const trail = d3.select("#sequence").append("svg:svg")
          .attr("width", this.width)
          .attr("height", 50)
          .attr("id", "trail");
      // Add the label at the end, for the percentage.
      trail.append("svg:text")
        .attr("id", "endlabel")
        .style("fill", "#000");
    },
    breadcrumbPoints(d, i) {
      const b = this.b;
      const points = [];

      points.push("0,0");
      points.push(b.w + ",0");
      points.push(b.w + b.t + "," + (b.h / 2));
      points.push(b.w + "," + b.h);
      points.push("0," + b.h);
      if (i > 0) { // Leftmost breadcrumb; don't include 6th vertex.
        points.push(b.t + "," + (b.h / 2));
      }
      return points.join(" ");
    },
    updateBreadcrumbs(nodeArray, percentageString) {
      const b = this.b;

      // Data join; key function combines name and depth (= position in sequence).
      const trail = d3.select("#trail")
          .selectAll("g")
          .data(nodeArray, function(d) { return d.data.name + d.depth; });

      // Remove exiting nodes.
      trail.exit().remove();

      // Add breadcrumb and label for entering nodes.
      const entering = trail.enter().append("svg:g");

      entering.append("svg:polygon")
          .attr("points", breadcrumbPoints)
          .style("fill", function(d) { return this.colors[d.data.name]; });

      entering.append("svg:text")
          .attr("x", (b.w + b.t) / 2)
          .attr("y", b.h / 2)
          .attr("dy", "0.35em")
          .attr("text-anchor", "middle")
          .text(function(d) { return d.data.name; });

      // Merge enter and update selections; set position for all nodes.
      entering.merge(trail).attr("transform", function(d, i) {
        return "translate(" + i * (b.w + b.s) + ", 0)";
      });

      // Now move and update the percentage at the end.
      d3.select("#trail").select("#endlabel")
          .attr("x", (nodeArray.length + 0.5) * (b.w + b.s))
          .attr("y", b.h / 2)
          .attr("dy", "0.35em")
          .attr("text-anchor", "middle")
          .text(percentageString);

      // Make the breadcrumb trail visible, if it's hidden.
      d3.select("#trail")
          .style("visibility", "");
    },
    drawLegend() {
      // Dimensions of legend item: width, height, spacing, radius of rounded rect.
      const li = {
        w: 75, h: 30, s: 3, r: 3
      };

      const legend = d3.select("#legend").append("svg:svg")
          .attr("width", li.w)
          .attr("height", d3.keys(this.colors).length * (li.h + li.s));

      const g = legend.selectAll("g")
          .data(d3.entries(this.colors))
          .enter().append("svg:g")
          .attr("transform", function(d, i) {
                  return "translate(0," + i * (li.h + li.s) + ")";
              });

      g.append("svg:rect")
          .attr("rx", li.r)
          .attr("ry", li.r)
          .attr("width", li.w)
          .attr("height", li.h)
          .style("fill", function(d) { return d.value; });

      g.append("svg:text")
          .attr("x", li.w / 2)
          .attr("y", li.h / 2)
          .attr("dy", "0.35em")
          .attr("text-anchor", "middle")
      .text(function(d) { return d.key; });
    },
    toggleLegend() {
      const legend = d3.select("#legend");
      if (legend.style("visibility") == "hidden") {
        legend.style("visibility", "");
      } else {
        legend.style("visibility", "hidden");
      }
    },
    buildHierarchy(csv) {
      const root = {
        "name": "root",
        "children": []
      };

      for (let i = 0; i < csv.length; i++) {
        let sequence = csv[i][0];
        let size = +csv[i][1];
        if (isNaN(size)) { // e.g. if this is a header row
          continue;
        }
        let parts = sequence.split("-");
        let currentNode = root;
        for (let j = 0; j < parts.length; j++) {
          let children = currentNode["children"];
          let nodeName = parts[j];
          let childNode;
          if (j + 1 < parts.length) {
      // Not yet at the end of the sequence; move down the tree.
      let foundChild = false;
      for (let k = 0; k < children.length; k++) {
        if (children[k]["name"] == nodeName) {
          childNode = children[k];
          foundChild = true;
          break;
        }
      }
      // If we don't already have a child node for this branch, create it.
      if (!foundChild) {
        childNode = {"name": nodeName, "children": []};
        children.push(childNode);
      }
      currentNode = childNode;
          } else {
      // Reached the end of the sequence; create a leaf node.
      childNode = {"name": nodeName, "size": size};
      children.push(childNode);
          }
        }
      }
      return root;
      // TODO
    },
  },
  mounted() {
    const width = this.width;
    const height = this.height;
    const b = this.b;

    this.colors = {
      "Disease": "#5687d1",
      "No Disease": "#7b615c",
      "Genetic Cohort PD": "#de783b",
      "Genetic Registry PD": "#6ab975",
      "Parkinson's Disease": "#a173d1",
      "SWEDD": "#bbbbbb",
      "GBA+": "#bbbbbb",
      "GBA-": "#bbbbbb",
      "LRRK2+": "#bbbbbb",
      "SNCA+": "#bbbbbb",
      "LRRK2-": "#bbbbbb",
      "HYP": "#bbbbbb",
      "RBD": "#bbbbbb",
    };

    const radius = Math.min(width, height) / 2;
    this.radius = radius;
    this.totalSize = 0;
    this.vis = d3.select('#chart').append('svg:svg')
      .attr("width", width)
      .attr("height", height)
      .append("svg:g")
      .attr("id", "container")
      .attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
    this.partition = partition()
      .size([2 * Math.Pi, radius * radius]);

    this.arc = arc()
      .startAngle(function(d) { return d.x0; })
      .endAngle(function(d) { return d.x1; })
      .innerRadius(function(d) { return Math.sqrt(d.y0); })
      .outerRadius(function(d) { return Math.sqrt(d.y1); });

    this.createVisualization(this.data);
  }


}
</script>

<style scoped>
body {
  font-family: 'Open Sans', sans-serif;
  font-size: 12px;
  font-weight: 400;
  background-color: #fff;
  width: 960px;
  height: 700px;
  margin-top: 10px;
}

#main {
  float: left;
  width: 750px;
}

#sidebar {
  float: right;
  width: 100px;
}

#sequence {
  width: 600px;
  height: 70px;
}

#legend {
  padding: 10px 0 0 3px;
}

#sequence text, #legend text {
  font-weight: 600;
  fill: #fff;
}

#chart {
  position: relative;
}

#chart path {
  stroke: #fff;
}

#explanation {
  position: absolute;
  top: 260px;
  left: 305px;
  width: 140px;
  text-align: center;
  color: #666;
  z-index: -1;
}

#percentage {
  font-size: 2.5em;
}
</style>
