read -p "site: " siteVar
cp -R ../../../templates/custom ../storeLocator/$siteVar
cp ../../../scripts/run_scraper.sh ../storeLocator/$siteVar/run_scraper.sh
cp ../../../scripts/validate.py ../storeLocator/$siteVar/validate.py
cd ../storeLocator/$siteVar
npm install
npm install axios jsdom
pip install phonenumbers==8.10.13
pip install zipcodes==1.0.5
pip install us==1.0.0
