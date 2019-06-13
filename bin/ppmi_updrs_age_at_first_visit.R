library(tidyverse)
library(lubridate)
ppmi <- read_tsv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi.tsv')

ppmi %>%
  separate(birthdate, into=c('birthday', 'birthyear'), sep='/') %>%
  separate(event_date, into=c('eventday', 'eventyear'), sep='/') %>%
  select(patient_id, birthyear, eventyear) %>%
  mutate(birthyear=as.integer(birthyear), eventyear=as.integer(eventyear)) %>%
  group_by(patient_id, birthyear) %>%
  summarise(first_visit=min(eventyear)) %>%
  mutate(age_at_first_visit=first_visit-birthyear) %>%
  select(patient_id, age_at_first_visit) %>%
  write_tsv('~/Projects/clio-vis/meeting/clio-vis/ppmi/ppmi_age_at_first_visit.tsv')
