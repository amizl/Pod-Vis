<template>
  <v-container fluid fill-height class="ma-0 pa-0" style="max-width: 425px;">
    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <div style="width: 280px; float: left;">
          Visit: {{ firstVisitLabel }}
        </div>
        <div>
          <p class="text-left">Visit: {{ lastVisitLabel }}</p>
        </div>
      </v-col>
    </v-row>

    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <!-- First Visit histogram -->
        <VerticalHistogram
          :id="`firstVisit-${dimensionName}`"
          left
          :dimension-name="`${variable.label} - First Visit`"
          :y-min="minValueBetweenDimensions"
          :y-domain="maxValueBetweenDimensions"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />

        <!-- Parallel Coordinates -->
        <canvas
          v-if="true"
          ref="canvas"
          :width="computedWidth"
          :height="computedHeight"
          :style="'padding: 0px; margin: 0px;'"
        >
        </canvas>

        <!-- Parallel Coordinates - SVG -->
        <svg
          v-if="false"
          ref="pcoords"
          :width="computedWidth"
          :height="computedHeight"
          :style="'padding: 0px; margin: 0px;'"
        ></svg>

        <!-- Last visit histogram -->
        <VerticalHistogram
          :id="`lastVisit-${dimensionName}`"
          :dimension-name="`${variable.label} - Last Visit`"
          :y-min="minValueBetweenDimensions"
          :y-domain="maxValueBetweenDimensions"
          :variable="variable"
          @userChangedVariable="userChangedVariable"
        />
      </v-col>
    </v-row>

    <v-row class="ma-0 pa-0">
      <v-col cols="12" class="ma-0 pa-0">
        <v-expansion-panels accordion>
          <v-expansion-panel>
            <v-expansion-panel-header>
              <v-simple-checkbox
                v-model="show_raw_data"
                hide-details
                class="shrink"
              />Show individual subjects
              <v-tooltip
                v-if="show_raw_data && subsample_data"
                top
                color="primary"
              >
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-badge
                      color="primary"
                      :content="subsample_labels[subsample_choice]"
                      class="pl-3"
                    ></v-badge>
                  </span>
                </template>
                <span
                  >Subsampling enabled: only
                  {{ subsample_labels[subsample_choice] }} of subjects are
                  shown</span
                >
              </v-tooltip>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="pl-3">
              <v-checkbox
                v-model="subsample_data"
                :disabled="!show_raw_data"
                hide-details
                dense
                label="Subsample:"
                class="pa-0 ma-0"
              />
              <v-slider
                v-model="subsample_choice"
                :disabled="!subsample_data || !show_raw_data"
                step="1"
                max="4"
                ticks="always"
                :tick-labels="subsample_labels"
              ></v-slider>
            </v-expansion-panel-content>
          </v-expansion-panel>

          <v-expansion-panel>
            <v-expansion-panel-header>
              <v-simple-checkbox
                v-model="draw_clusters"
                hide-details
                class="shrink"
              />Show clusters
              <v-tooltip v-if="draw_clusters" top color="primary">
                <template v-slot:activator="{ on: tooltip }">
                  <span v-on="{ ...tooltip }">
                    <v-badge
                      color="primary"
                      :content="num_clusters_displayed + '/' + num_clusters"
                      class="pl-3"
                    ></v-badge>
                  </span>
                </template>
                <span
                  >Displaying {{ num_clusters_displayed }} of
                  {{ num_clusters }} clusters</span
                >
              </v-tooltip>
            </v-expansion-panel-header>
            <v-expansion-panel-content class="pl-3">
              <v-combobox
                v-model="cluster_choice"
                :disabled="!draw_clusters"
                :items="cluster_choices"
                label="Clusters"
                dense
              ></v-combobox>

              <v-combobox
                v-model="cluster_style_choice"
                :disabled="!draw_clusters"
                :items="cluster_style_choices"
                label="Cluster display style"
                dense
              ></v-combobox>

              <v-slider
                v-model="min_cluster_size"
                :disabled="!draw_clusters"
                label="Min. cluster size:"
                thumb-label="always"
                thumb-size="24"
                :min="1"
                :max="unfilteredData.length"
                hide-details
                dense
                class="pt-4"
              >
              </v-slider>
            </v-expansion-panel-content>
          </v-expansion-panel>
        </v-expansion-panels>
      </v-col>
    </v-row>
  </v-container>
</template>

<script>
import { mapActions, mapState } from 'vuex';
import { state, actions } from '@/store/modules/cohortManager/types';
import { scaleLinear } from 'd3-scale';
import { select } from 'd3-selection';
import { min, max, mean, deviation } from 'd3-array';
import { colors, hexToRgbA } from '@/utils/colors';
import VerticalHistogram from '@/components/CohortManager/VerticalHistogram/VerticalHistogram.vue';

export default {
  directives: {
    dimension(el, binding) {
      const axisMethod = binding.value;
      select(el)
        .transition()
        .call(axisMethod);
    },
  },
  components: {
    VerticalHistogram,
  },
  props: {
    dimensionName: {
      type: Number,
      required: true,
    },
    variable: {
      type: Object,
      required: true,
    },
    firstVisitLabel: {
      type: String,
      required: false,
      default: 'First Visit',
    },
    lastVisitLabel: {
      type: String,
      required: false,
      default: 'Last Visit',
    },
    subsamplingMin: {
      type: Number,
      required: false,
      default: 500,
    },
  },
  data() {
    return {
      width: 0,
      height: 0,
      margin: { top: 20, right: 0, bottom: 10, left: 0 },
      mounted: false,
      show_raw_data: true,
      subsample_data: false,
      draw_clusters: false,
      subsample_labels: ['1%', '5%', '10%', '20%', '50%'],
      subsample_choice: 2,
      min_cluster_size: 1,
      cluster_choice: 'Change/baseline',
      cluster_choices: [
        'Change/baseline',
        'Change',
        'First Visit',
        'Last Visit',
      ],
      cluster_style_choice: 'Average +/- 1 SD',
      cluster_style_choices: [
        'Average (width=n_subjects)',
        'Average +/- 1 SD',
        'Average + all subjects',
      ],
      num_clusters: 0,
      num_clusters_displayed: 0,
    };
  },
  computed: {
    ...mapState('cohortManager', {
      filteredData: state.FILTERED_DATA,
      unfilteredData: state.UNFILTERED_DATA,
      highlightedSubset: state.HIGHLIGHTED_SUBSET,
      dimensions: state.DIMENSIONS,
    }),
    populationData() {
      return this.unfilteredData.map(d => d[this.dimensionName]);
    },
    cohortData() {
      return this.filteredData.map(d => d[this.dimensionName]);
    },
    subsampledPopulationData() {
      return this.subsample(this.unfilteredData).map(
        d => d[this.dimensionName]
      );
    },
    subsampledCohortData() {
      return this.subsample(this.filteredData).map(d => d[this.dimensionName]);
    },
    nonCohortData() {
      var cohortSubIds = {};
      this.filteredData.forEach(d => {
        cohortSubIds[d['subject_id']] = 1;
      });
      var nonCohortData = [];
      this.unfilteredData.forEach(d => {
        if (!(d['subject_id'] in cohortSubIds)) {
          nonCohortData.push(d);
        }
      });
      return nonCohortData.map(d => d[this.dimensionName]);
    },
    populationPaths() {
      var data = this.subsample_data
        ? this.subsampledPopulationData
        : this.populationData;
      return data.map(d => {
        const firstVisitCoordinates = {
          x: this.xDimensionScale('First Visit'),
          y: this.dimensionScale(d.firstVisit),
        };
        const lastVisitCoordinates = {
          x: this.xDimensionScale('Last Visit'),
          y: this.dimensionScale(d.lastVisit),
        };
        return {
          firstVisitCoordinates,
          lastVisitCoordinates,
        };
      });
    },
    cohortPaths() {
      var data = this.subsample_data
        ? this.subsampledCohortData
        : this.cohortData;
      return data.map(d => {
        const firstVisitCoordinates = {
          x: this.xDimensionScale('First Visit'),
          y: this.dimensionScale(d.firstVisit),
        };
        const lastVisitCoordinates = {
          x: this.xDimensionScale('Last Visit'),
          y: this.dimensionScale(d.lastVisit),
        };
        return {
          firstVisitCoordinates,
          lastVisitCoordinates,
        };
      });
    },
    nonCohortPaths() {
      return this.nonCohortData.map(d => {
        const firstVisitCoordinates = {
          x: this.xDimensionScale('First Visit'),
          y: this.dimensionScale(d.firstVisit),
        };
        const lastVisitCoordinates = {
          x: this.xDimensionScale('Last Visit'),
          y: this.dimensionScale(d.lastVisit),
        };
        return {
          firstVisitCoordinates,
          lastVisitCoordinates,
        };
      });
    },
    minValueBetweenDimensions() {
      const firstMin = min(this.populationData, d => d.firstVisit);
      const lastMin = min(this.populationData, d => d.lastVisit);
      return Math.min(firstMin, lastMin);
    },
    maxValueBetweenDimensions() {
      const firstMax = max(this.populationData, d => d.firstVisit);
      const lastMax = max(this.populationData, d => d.lastVisit);
      return Math.max(firstMax, lastMax);
    },
    computedWidth() {
      const { left, right } = this.margin;
      const { width } = this;
      return width - left - right;
    },
    computedHeight() {
      const { height } = this;
      return height;
    },
    dimensionScale() {
      const scale = scaleLinear()
        .domain(
          this.variable.flip_axis
            ? [this.minValueBetweenDimensions, this.maxValueBetweenDimensions]
            : [this.maxValueBetweenDimensions, this.minValueBetweenDimensions]
        )
        .range([this.margin.top, this.computedHeight - this.margin.bottom]);
      return scale;
    },
  },
  watch: {
    cohortData() {
      this.$nextTick(() => this.updateCanvas());
    },
    highlightedSubset() {
      this.$nextTick(() => this.updateCanvas());
    },
    subsample_choice() {
      this.$nextTick(() => this.updateCanvas());
    },
    cluster_choice() {
      this.$nextTick(() => this.updateCanvas());
    },
    cluster_style_choice() {
      this.$nextTick(() => this.updateCanvas());
    },
    show_raw_data() {
      this.$nextTick(() => this.updateCanvas());
    },
    subsample_data() {
      this.$nextTick(() => this.updateCanvas());
    },
    draw_clusters() {
      this.$nextTick(() => this.updateCanvas());
    },
    min_cluster_size() {
      this.$nextTick(() => this.updateCanvas());
    },
  },
  created() {
    var udl = this.unfilteredData.length;
    if (udl > this.subsamplingMin) {
      // try to keep # of subjects < 1000
      if (udl >= 1000 * 100) {
        this.subsample_choice = 0; // 1%
      } else if (udl >= 1000 * 10) {
        this.subsample_choice = 1; // 5%
      } else if (udl >= 1000 * 5) {
        this.subsample_choice = 2; // 10%
      } else if (udl >= 1000 * 2) {
        this.subsample_choice = 3; // 20%
      } else {
        this.subsample_choice = 4; // 50%
      }
      this.subsample_data = true;
    }
  },
  mounted() {
    this.container = this.$refs.container;
    this.canvas = this.$refs.canvas;
    this.context = select(this.canvas)
      .node()
      .getContext('2d');

    // Resize chart so we have parent dimensions (width/height)
    this.resizeChart();
    this.mounted = true;

    this.$nextTick(() => this.updateCanvas());
  },
  methods: {
    ...mapActions('cohortManager', {
      addDimension: actions.ADD_DIMENSION,
    }),
    userChangedVariable() {
      this.$emit('userChangedVariable');
    },
    resizeChart() {
      this.height = 300;
      this.width = 140;
    },
    subsample(old) {
      var sampled = [];
      var delta = [100, 20, 10, 5, 2][this.subsample_choice];
      if (delta == 1) return old;
      for (var i = 0; i < old.length; i += delta) {
        sampled.push(old[i]);
      }
      return sampled;
    },
    xDimensionScale(visit) {
      return visit == 'First Visit' ? 0 : this.computedWidth;
    },
    drawCurve({ firstVisitCoordinates, lastVisitCoordinates }) {
      const { context } = this;
      context.beginPath();
      context.moveTo(firstVisitCoordinates.x, firstVisitCoordinates.y);
      context.bezierCurveTo(
        firstVisitCoordinates.x +
          (lastVisitCoordinates.x - firstVisitCoordinates.x) / 4,
        firstVisitCoordinates.y,
        lastVisitCoordinates.x -
          (lastVisitCoordinates.x - firstVisitCoordinates.x) / 4,
        lastVisitCoordinates.y,
        lastVisitCoordinates.x,
        lastVisitCoordinates.y
      );
      context.stroke();
    },
    drawUnfiltered(color) {
      const { context } = this;
      context.lineWidth = 1;
      context.strokeStyle = color;
      context.globalAlpha = 1;
      this.populationPaths.forEach(path => this.drawCurve(path));
    },
    drawFiltered() {
      const { context } = this;
      context.lineWidth = 1;
      context.globalAlpha = 0.45;

      if (this.highlightedSubset === 'cohort') {
        context.strokeStyle = colors['cohort'];
        this.cohortPaths.forEach(path => this.drawCurve(path));
      } else {
        context.strokeStyle = colors['nonCohort'];
        this.nonCohortPaths.forEach(path => this.drawCurve(path));
      }
    },
    drawPopulationClusters() {
      var pclust = this.computeFiveClusters(this.unfilteredData);
      this.num_clusters_displayed = pclust.length;

      var popColor = colors['population'];
      var cohortColor = colors['cohort'];

      // interpolate color between population color and cohort color based
      // on fraction of cluster subjects in the cohort
      var pc = hexToRgbA(popColor);
      var cc = hexToRgbA(cohortColor);
      var pcd = [cc[0] - pc[0], cc[1] - pc[1], cc[2] - pc[2]];

      const { context } = this;
      context.globalAlpha = 1;

      var fv_x = this.xDimensionScale('First Visit');
      var lv_x = this.xDimensionScale('Last Visit');

      var ht = this.computedHeight - this.margin.bottom;
      var ns = this.unfilteredData.length;

      pclust.forEach(c => {
        var fv_y = this.dimensionScale(c['avg_f']);
        var lv_y = this.dimensionScale(c['avg_l']);

        // interpolated color
        var cf = c['cohort_frac'];
        var col = [
          pc[0] + cf * pcd[0],
          pc[1] + cf * pcd[1],
          pc[2] + cf * pcd[2],
        ];
        var ccol = 'rgb(' + col.join(',') + ',0.7)';

        var bcurve = function(context, fv_x, fv_y, lv_x, lv_y) {
          context.bezierCurveTo(
            fv_x + (lv_x - fv_x) / 4,
            fv_y,
            lv_x - (lv_x - fv_x) / 4,
            lv_y,
            lv_x,
            lv_y
          );
        };

        var fv_ymin, fv_ymax, lv_ymin, lv_ymax;

        // OPTION 1: draw line around average with thickness determined by number of subjects
        if (this.cluster_style_choice == this.cluster_style_choices[0]) {
          context.beginPath();
          context.moveTo(fv_x, fv_y);
          bcurve(context, fv_x, fv_y, lv_x, lv_y);
          context.lineWidth = (c['data'].length / ns) * ht * 0.1;
          context.strokeStyle = ccol;
          context.stroke();
        }
        // OPTION 2: draw average line +/- 1 SD
        else if (this.cluster_style_choice == this.cluster_style_choices[1]) {
          // +1 SD
          fv_ymax = this.dimensionScale(c['avg_f'] + c['deviation_f']);
          lv_ymax = this.dimensionScale(c['avg_l'] + c['deviation_l']);

          // -1 SD
          fv_ymin = this.dimensionScale(c['avg_f'] - c['deviation_f']);
          lv_ymin = this.dimensionScale(c['avg_l'] - c['deviation_l']);

          context.lineWidth = 1;

          // fill area from +1 SD to -1 SD
          context.beginPath();
          context.moveTo(fv_x, fv_ymax);
          bcurve(context, fv_x, fv_ymax, lv_x, lv_ymax);
          context.lineTo(lv_x, lv_ymin);
          bcurve(context, lv_x, lv_ymin, fv_x, fv_ymin);
          context.lineTo(fv_x, fv_ymax);
          context.fillStyle = 'rgb(208,208,208,0.3)';
          context.fill();

          context.strokeStyle = ccol;

          // +1 SD
          context.beginPath();
          context.moveTo(fv_x, fv_ymax);
          bcurve(context, fv_x, fv_ymax, lv_x, lv_ymax);
          context.stroke();

          // -1 SD
          context.beginPath();
          context.moveTo(fv_x, fv_ymin);
          bcurve(context, fv_x, fv_ymin, lv_x, lv_ymin);
          context.stroke();

          // average, width = num clusters
          context.lineWidth = (c['data'].length / ns) * ht * 0.1;
          context.beginPath();
          context.moveTo(fv_x, fv_y);
          bcurve(context, fv_x, fv_y, lv_x, lv_y);
          context.stroke();
        }
        // OPTION 3: draw average line plus entire area around min/max
        else if (this.cluster_style_choice == this.cluster_style_choices[2]) {
          // max
          fv_ymax = this.dimensionScale(c['max_f']);
          lv_ymax = this.dimensionScale(c['max_l']);

          // min
          fv_ymin = this.dimensionScale(c['min_f']);
          lv_ymin = this.dimensionScale(c['min_l']);

          context.beginPath();
          context.strokeStyle = '#000';

          context.moveTo(fv_x, fv_ymin);
          context.lineWidth = 0;
          context.lineTo(fv_x, fv_ymax);
          context.lineWidth = 1;
          context.bezierCurveTo(
            fv_x + (lv_x - fv_x) / 4,
            fv_ymax,
            lv_x - (lv_x - fv_x) / 4,
            lv_ymax,
            lv_x,
            lv_ymax
          );

          context.lineWidth = 0;
          context.lineTo(lv_x, lv_ymin);
          context.lineWidth = 1;
          context.bezierCurveTo(
            lv_x - (lv_x - fv_x) / 4,
            lv_ymin,
            fv_x + (lv_x - fv_x) / 4,
            fv_ymin,
            fv_x,
            fv_ymin
          );

          context.fillStyle = 'rgb(208,208,208,0.3)';
          context.fill();

          // trace outlines
          context.strokeStyle = ccol;
          context.beginPath();
          context.moveTo(fv_x, fv_ymax);
          context.bezierCurveTo(
            fv_x + (lv_x - fv_x) / 4,
            fv_ymax,
            lv_x - (lv_x - fv_x) / 4,
            lv_ymax,
            lv_x,
            lv_ymax
          );
          context.moveTo(lv_x, lv_ymin);
          context.bezierCurveTo(
            lv_x - (lv_x - fv_x) / 4,
            lv_ymin,
            fv_x + (lv_x - fv_x) / 4,
            fv_ymin,
            fv_x,
            fv_ymin
          );
          context.stroke();

          // average, width = num clusters
          context.lineWidth = (c['data'].length / ns) * ht * 0.1;
          context.beginPath();
          context.moveTo(fv_x, fv_y);
          bcurve(context, fv_x, fv_y, lv_x, lv_y);
          context.stroke();
        }
      });
    },
    updateCanvas() {
      if (!this.mounted) return;

      this.context.clearRect(0, 0, this.width, this.height);
      // individual subjects
      if (this.show_raw_data) {
        if (this.unfilteredData.length > this.filteredData.length) {
          this.drawUnfiltered(colors['population']);
        }
        this.drawFiltered();
      }
      // clusters of subjects
      if (this.draw_clusters) {
        this.drawPopulationClusters();
      }
    },
    _addToCluster(cluster, d) {
      cluster['data'].push(d);

      if (!('sum_f' in cluster)) cluster['sum_f'] = 0;
      if (!('sum_l' in cluster)) cluster['sum_l'] = 0;

      var f = d[this.dimensionName]['firstVisit'];
      var l = d[this.dimensionName]['lastVisit'];

      if (!('min_f' in cluster) || f < cluster['min_f']) cluster['min_f'] = f;
      if (!('max_f' in cluster) || f > cluster['max_f']) cluster['max_f'] = f;
      cluster['sum_f'] += d[this.dimensionName]['firstVisit'];

      if (!('min_l' in cluster) || l < cluster['min_l']) cluster['min_l'] = l;
      if (!('max_l' in cluster) || l > cluster['max_l']) cluster['max_l'] = l;
      cluster['sum_l'] += d[this.dimensionName]['lastVisit'];
    },
    _updateClusters(clusters) {
      var fd = this.filteredData;
      var dname = this.dimensionName;

      // index subjects in filteredData
      var fsh = {};
      fd.forEach(d => {
        fsh[d['subject_id']] = true;
      });

      clusters.forEach(c => {
        c['avg_f'] = c['sum_f'] / c['data'].length;
        c['avg_l'] = c['sum_l'] / c['data'].length;
        c['num_in_cohort'] = 0;
        c['data'].forEach(d => {
          if (d['subject_id'] in fsh) {
            c['num_in_cohort'] += 1;
          }
        });
        c['cohort_frac'] = c['num_in_cohort'] / c['data'].length;

        var fv_values = c['data'].map(d => d[dname]['firstVisit']);
        var lv_values = c['data'].map(d => d[dname]['lastVisit']);

        c['deviation_f'] = deviation(fv_values);
        c['deviation_l'] = deviation(lv_values);

        //        console.log('avg_f=' + c['avg_f'] + ' mean_f=' + mean(fv_values));
        //        console.log('avg_l=' + c['avg_l'] + ' mean_l=' + mean(lv_values));
      });
    },
    // compute five clusters: >3 SD,1-3 SD,-1 - +1 SD,-1 - -3 SD,< 3 SD
    computeFiveClusters(data) {
      var dname = this.dimensionName;
      var val_fn = null;

      if (this.cluster_choice == this.cluster_choices[0]) {
        val_fn = function(d) {
          return d[dname]['change'] / d[dname]['firstVisit'];
        };
      } else if (this.cluster_choice == this.cluster_choices[1]) {
        val_fn = function(d) {
          return d[dname]['change'];
        };
      } else if (this.cluster_choice == this.cluster_choices[2]) {
        val_fn = function(d) {
          return d[dname]['firstVisit'];
        };
      } else if (this.cluster_choice == this.cluster_choices[3]) {
        val_fn = function(d) {
          return d[dname]['lastVisit'];
        };
      }

      var values = data.map(d => val_fn(d));
      var mn = mean(values);
      var dev = deviation(values);

      var p3sd = mn + 3 * dev;
      var m3sd = mn - 3 * dev;
      var p1sd = mn + dev;
      var m1sd = mn - dev;

      var clusters = [
        { data: [] }, // +3 SD or more
        { data: [] }, // +1 - +3 SD
        { data: [] }, // +1 - -1 SD
        { data: [] }, // -1 - -3 SD
        { data: [] }, // -3 SD or more
      ];

      data.forEach(d => {
        var val = val_fn(d);
        if (val > p3sd) {
          this._addToCluster(clusters[0], d);
        } else if (val > p1sd) {
          this._addToCluster(clusters[1], d);
        } else if (val >= m1sd) {
          this._addToCluster(clusters[2], d);
        } else if (val >= m3sd) {
          this._addToCluster(clusters[3], d);
        } else {
          this._addToCluster(clusters[4], d);
        }
      });

      // don't count zero size clusters
      clusters = clusters.filter(c => c.data.length > 0);

      this.num_clusters = clusters.length;
      clusters = clusters.filter(c => c.data.length >= this.min_cluster_size);
      this._updateClusters(clusters);
      return clusters;
    },
    // deprecated - this is clustering subjects by last visit proximity only
    getPopulationClusters() {
      var ud = this.unfilteredData;
      var fd = this.filteredData;

      // index subjects in filteredData
      var fsh = {};
      fd.forEach(d => {
        fsh[d['subject_id']] = true;
      });

      // TODO - compute cohort fraction

      var maxGap = 1; // TODO - set to fraction of range

      // sort by increasing last visit
      var uds = ud.sort(
        (a, b) =>
          a[this.dimensionName]['lastVisit'] -
          b[this.dimensionName]['lastVisit']
      );
      var clusters = [];
      var cluster = null;
      var dname = this.dimensionName;

      uds.forEach(d => {
        // new cluster
        if (
          cluster == null ||
          d[dname]['lastVisit'] - cluster['last'][dname]['lastVisit'] > maxGap
        ) {
          cluster = {
            data: [d],
            last: d,
            min_f: d[dname]['firstVisit'],
            max_f: d[dname]['firstVisit'],
            sum_f: d[dname]['firstVisit'],
            min_l: d[dname]['lastVisit'],
            max_l: d[dname]['lastVisit'],
            sum_l: d[dname]['lastVisit'],
            num_in_cohort: 0,
          };
          clusters.push(cluster);
        }
        // add to last cluster
        else {
          cluster['data'].push(d);
          cluster['last'] = d;
          cluster['max_l'] = d[dname]['lastVisit'];
          cluster['sum_l'] += d[dname]['lastVisit'];
          var x = d[dname]['firstVisit'];
          if (x < cluster['min_f']) cluster['min_f'] = x;
          if (x > cluster['max_f']) cluster['max_f'] = x;
          cluster['sum_f'] += d[dname]['firstVisit'];
        }
        if (d['subject_id'] in fsh) {
          cluster['num_in_cohort'] += 1;
        }
      });

      clusters.forEach(c => {
        c['avg_f'] = c['sum_f'] / c['data'].length;
        c['avg_l'] = c['sum_l'] / c['data'].length;

        //console.log("num in cohort = " + c['num_in_cohort'] + " data length = " + c['data'].length);

        c['cohort_frac'] = c['num_in_cohort'] / c['data'].length;
        //        console.log(
        //          'cluster of size ' + c['data'].length +
        //          ' min_f=' + c['min_f'] +
        //          ' max_f=' + c['max_f'] +
        //          ' min_l=' + c['min_l'] +
        //          ' max_l=' + c['max_l'] +
        //          ' cohort_frac=' + c['cohort_frac']
        //        );
      });

      this.num_clusters = clusters.length;
      clusters = clusters.filter(
        c => c['data'].length >= this.min_cluster_size
      );

      return clusters;
    },
    subsampleClicked(e) {
      e.cancelBubble = true;
    },
  },
};
</script>

<style lang="scss" scoped></style>
