#!/bin/bash

TODAY=$(date +%F_%H%M%S)

git pull #gets any updates to the reports in the data directory

grinch -t 10 -i grinch/data/config.yaml --outdir $TODAY --output-prefix global_report

cp $TODAY/report/global_report_B.1.1.7.html /home/shared/lineages-website/data/global_report.B.1.1.7.html
cp $TODAY/report/global_report_B.1.351.html /home/shared/lineages-website/data/global_report.B.1.351.html
cp $TODAY/report/global_report_P.1.html /home/shared/lineages-website/data/global_report.P.1.html

cp $TODAY/figures/Map_of_B.1.351_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_B.1.351_local_transmission.svg
cp $TODAY/figures/Map_of_B.1.1.7_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_B.1.1.7_local_transmission.svg
cp $TODAY/figures/Map_of_P.1_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_P.1_local_transmission.svg

cp $TODAY/2/lineages.metadata.csv /home/shared/lineages-website/_data/lineages.metadata.csv

update_website.py --website-dir /home/shared/lineages-website -m $TODAY/2/lineages.metadata.csv -n /home/shared/pangoLEARN/pangoLEARN/supporting_information/lineage_notes.txt -o /home/shared/lineages-website/_data/lineage_data.json


cd /home/shared/lineages-website
git add _data/global_report_*.html
git add _data/lineages.metadata.csv
git add _data/lineage_data.json
git add assets/images/Map_of*loca*
git add lineages/lineage*
git add lineages.md

git commit -m "updating new variant report and website $TODAY"
git push

