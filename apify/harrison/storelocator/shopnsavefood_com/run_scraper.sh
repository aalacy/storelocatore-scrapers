domain=${PWD##*/}
scraper_name=${domain}-scraper
docker build -t $scraper_name --no-cache .
rm -rf apify_docker_storage
docker run -e "APIFY_TOKEN=''" -e "APIFY_LOCAL_STORAGE_DIR=apify_storage" -v /Users/tenzing/code/crawl-service/apify/harrison/storelocator/shopnsavefood_com/apify_docker_storage:/apify_storage ${scraper_name}:latest
