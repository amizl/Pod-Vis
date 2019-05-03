<template lang="pug">
  v-container(fluid fill-height)
    v-layout(align-center justify-center)
      categorical-card(
        :measure='measure'
        :label='label'
        :data='filtered'
      )

</template>

<script>
import CategoricalCard from '@/components/CohortManager/CategoricalCard.vue';

export default {
  components: {
    CategoricalCard,
  },
  data() {
    return {
      measure: 'updrs_1',
      label: 'Intellectual Impairment',
      // data: [{"measure":"updrs_17","label":"sensory complaints related to parkinsonism","cohort":"female","1":2328,"2":543,"3":282,"4":115,"5":12},{"measure":"updrs_17","label":"sensory complaints related to parkinsonism","cohort":"male","1":1242,"2":348,"3":224,"4":97,"5":12},{"measure":"updrs_17","label":"sensory complaints related to parkinsonism","cohort":"population","1":3570,"2":891,"3":506,"4":212,"5":24},{"measure":"updrs_22ll","label":"left lower limb rigidity","cohort":"female","1":3086,"2":2285,"3":1068,"4":202,"5":31},{"measure":"updrs_22ll","label":"left lower limb rigidity","cohort":"male","1":2271,"2":1188,"3":419,"4":82,"5":22},{"measure":"updrs_22ll","label":"left lower limb rigidity","cohort":"population","1":5357,"2":3473,"3":1487,"4":284,"5":53},{"measure":"updrs_22lu","label":"left upper limb rigidity","cohort":"female","1":1201,"2":3346,"3":1949,"4":235,"5":24},{"measure":"updrs_22lu","label":"left upper limb rigidity","cohort":"male","1":1134,"2":1974,"3":817,"4":95,"5":17},{"measure":"updrs_22lu","label":"left upper limb rigidity","cohort":"population","1":2335,"2":5320,"3":2766,"4":330,"5":41},{"measure":"updrs_25l","label":"left rapid alternating movement of hands","cohort":"female","1":1322,"2":2892,"3":1990,"4":537,"5":88},{"measure":"updrs_25l","label":"left rapid alternating movement of hands","cohort":"male","1":794,"2":1686,"3":1208,"4":359,"5":52},{"measure":"updrs_25l","label":"left rapid alternating movement of hands","cohort":"population","1":2116,"2":4578,"3":3198,"4":896,"5":140},{"measure":"updrs_5","label":"speech","cohort":"female","1":900,"2":1191,"3":912,"4":277,"5":32},{"measure":"updrs_5","label":"speech","cohort":"male","1":843,"2":603,"3":356,"4":126,"5":12},{"measure":"updrs_5","label":"speech","cohort":"population","1":1743,"2":1794,"3":1268,"4":403,"5":44}],
      // data: [{"measure":"updrs_1","label":"intellectual impairment","cohort":"female","1":3810,"2":1899,"3":648,"4":141,"5":32},{"measure":"updrs_1","label":"intellectual impairment","cohort":"male","1":2313,"2":1192,"3":325,"4":66,"5":28},{"measure":"updrs_1","label":"intellectual impairment","cohort":"population","1":6123,"2":3091,"3":973,"4":207,"5":60}]
    };
  },
  computed: {
    filtered() {
      return this.data.filter(d => d.measure === this.measure);
    },
  },
};
</script>

<style scoped></style>
