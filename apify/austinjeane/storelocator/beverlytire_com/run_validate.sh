base_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo $base_path
domain=${PWD##*/}
echo $domain
scraper_name=${domain}_validate
docker build -f validate.Dockerfile -t $scraper_name --no-cache .
rm -rf validate
docker rm $scraper_name
docker run --name $scraper_name ${scraper_name}:latest
docker cp ${scraper_name}:/app/SUCCESS "${base_path}/SUCCESS"
