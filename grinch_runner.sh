#!/bin/bash
source /home/s1680070/.bashrc_conda
conda activate grinch

TODAY=$(date +%F_%H%M%S)
echo "running $TODAY report"
cd /home/shared/grinch && git pull #gets any updates to the reports in the data directory

python setup.py install

grinch -t 40 -i /home/shared/grinch/grinch/data/config.yaml --outdir "/home/shared/$TODAY" --output-prefix global_report

cd /home/shared/lineages-website && git pull

python /home/shared/grinch/grinch/scripts/update_website.py --website-dir /home/shared/lineages-website -m /home/shared/$TODAY/2/lineages.metadata.csv -n /home/shared/pangoLEARN/pangoLEARN/supporting_information/lineage_notes.txt -o /home/shared/lineages-website/_data/lineage_data.json

cp /home/shared/$TODAY/report/global_report_B.1.1.7.html /home/shared/lineages-website/global_report_B.1.1.7.html
cp /home/shared/$TODAY/report/global_report_B.1.351.html /home/shared/lineages-website/global_report_B.1.351.html
cp /home/shared/$TODAY/report/global_report_P.1.html /home/shared/lineages-website/global_report_P.1.html

cp /home/shared/$TODAY/figures/Map_of_B.1.351_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_B.1.351_local_transmission.svg
cp /home/shared/$TODAY/figures/Map_of_B.1.1.7_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_B.1.1.7_local_transmission.svg
cp /home/shared/$TODAY/figures/Map_of_P.1_local_transmission.svg /home/shared/lineages-website/assets/images/Map_of_P.1_local_transmission.svg

cp /home/shared/$TODAY/2/lineages.metadata.csv /home/shared/lineages-website/_data/lineages.metadata.csv

cd /home/shared/lineages-website && git pull

git add /home/shared/lineages-website/global_report_*.html
git add /home/shared/lineages-website/_data/lineages.metadata.csv
git add /home/shared/lineages-website/_data/lineage_data.json
git add /home/shared/lineages-website/assets/images/Map_of*loca*

git commit -m "updating new variant report $TODAY"
git push

