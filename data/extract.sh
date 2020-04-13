for i in winnow_demographics_long.csv winnow_obs_long.csv winnow_obs_summary.csv
    do echo $i
    cat $i | awk 'BEGIN {FS=","}; NR==1 {print $0}; {if($1 == "245" || $1 == "432") {print $0}}' > ../${i} 
done
