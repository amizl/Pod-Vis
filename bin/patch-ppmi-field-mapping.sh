#!/bin/bash

# Usage: patch-ppmi-field-mapping.sh data/ppmi_field_mapping.csv

echo "patching $1"

perl -pi.bak -e 's/Number sequencing/Number Sequencing/g; s/REM Sleep Disorder/REM Sleep Behavior Disorder Questionnaire/g; s/Symbol Digit Modality/Symbol Digit Modalities/g; s/Geriatric Depression State Score/Geriatric Depression Scale Score/g; s/Geriatric Depression State/Geriatric Depression Scale State/g;s/HealthSummary/Disease Features/g;' $1


