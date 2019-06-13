<template>
  <!-- <rect
    :x="x"
    :y="useTweeningYIfNotFalsy"
    :width="width"
    :height="useTweeningHeightIfNotFalsy"
    :fill="fill"
  ></rect> -->
  <rect
    :transform="`translate(${xScale(bin.x0)}, ${yScale(bin.length)})`"
    :width="xScale(bin.x1) - xScale(bin.x0) - 1"
    :height="h - yScale(bin.length)"
    fill="#3F51B5"
  />
</template>

<script>
import TWEEN from '@tweenjs/tween.js';

export default {
  props: {
    x: {
      type: Number,
      required: true,
    },
    y: {
      type: Number,
      required: true,
      default: 0,
    },
    // ystart: {
    //   type: Number,
    //   required: true,
    //   default: 0,
    // },
    width: {
      type: Number,
      required: true,
    },
    height: {
      type: Number,
      required: true,
      default: 0,
    },
    fill: {
      type: String,
      required: true,
    },
  },
  data() {
    return {
      tweeningHeight: 0,
      tweeningY: 0,
    };
  },
  computed: {
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningYIfNotFalsy() {
      return this.tweeningY ? this.tweeningY : this.y;
    },
    /**
     * We only want to use tweening variable after the bar is already
     * drawn with the Y variable
     */
    useTweeningHeightIfNotFalsy() {
      return this.tweeningHeight ? this.tweeningHeight : this.height;
    },
  },
  watch: {
    height(newValue, oldValue) {
      // When the height changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningHeight');
    },
    y(newValue, oldValue) {
      // When the Y changes, tween from the old value to the new
      this.tween(oldValue, newValue, 'tweeningY');
    },
  },
  methods: {
    /**
     * Method to tween from one value to another
     */
    tween(startValue, endValue, prop) {
      var vm = this;
      function animate() {
        if (TWEEN.update()) {
          requestAnimationFrame(animate);
        }
      }
      new TWEEN.Tween({ tweeningValue: startValue })
        .to({ tweeningValue: endValue }, 500)
        .easing(TWEEN.Easing.Quadratic.Out)
        .onUpdate(({ tweeningValue }) => {
          vm[prop] = tweeningValue;
        })
        .start();
      animate();
    },
  },
};
</script>

<style scoped>
rect {
  cursor: pointer;
}
</style>
