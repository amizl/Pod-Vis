library(tidyverse)

ppmi <- read_tsv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi.tsv')

updrsTotals <- ppmi %>%
  filter(str_detect(scale, 'UPDRS')) %>%
  group_by(patient_id, disease, event_date, event, scale) %>%
  summarise(
    n_NAs=sum(is.na(score)),
    n_measures=n(), 
    na_percentage=(n_NAs / n_measures) * 100,
    partTotal=ifelse(
      na_percentage <= 20, 
      sum(score, na.rm=TRUE) / (n_measures - n_NAs) * n_measures,
      NA
    )
  ) %>% 
  group_by(patient_id, disease,  event_date, event) %>%
  mutate(totalUPDRS = sum(partTotal)) %>%
  select(patient_id, disease, event_date, event, totalUPDRS) %>%
  group_by(patient_id, event_date) %>%
  distinct() %>%
  mutate(scale='MDS-UPDRS Total') %>%
  rename(score=totalUPDRS)



ids <- updrsTotals %>%
  group_by(patient_id, event) %>%
  tally() %>%
  filter(n > 1) %>%
  select(patient_id)


updrsTotals %>% filter(patient_id %in% ids$patient_id) %>% View()

updrsTotals %>%
  write_tsv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi_updrs_total.tsv')