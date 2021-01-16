TODAY = $(date +%F_%H%M%S)

cd grinch
conda activate grinch
git pull #gets any updates to the reports in the data directory
python setup.py install #install any updates

grinch -t 10 -i grinch/data/config.yaml --outdir $TODAY --output-prefix global_report

cp $TODAY/report/global_report_B.1.1.7.html /home/shared/lineages-website/data/global_report.B.1.1.7.html
cp $TODAY/report/global_report_B.1.351.html /home/shared/lineages-website/data/global_report.B.1.351.html

cd /home/shared/lineages-website
git add _data/global_report_B.1*
git commit -m "updating new variant report $TODAY"
git push
