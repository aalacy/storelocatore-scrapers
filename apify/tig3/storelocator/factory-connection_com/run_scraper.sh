# Enable debug mode
if [[ "$1" == "--debug" ]]; then
  EXTRA_PARAMS='-it --entrypoint /bin/bash'
fi

base_path="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
domain=${PWD##*/}
scraper_name=${domain}-scraper

PWD_SET=$(if [[ -z $PROXY_PASSWORD ]]; then echo ""; else echo "< NON-EMPTY >"; fi)
GAK_SET=$(if [[ -z $GOOGLE_API_KEY ]]; then echo ""; else echo "< NON-EMPTY >"; fi)

echo "-----------------"
echo "BUILDING AND RUNNING DOCKER IMG [$scraper_name:latest] WITH:"
echo
echo "PROXY_URL=$PROXY_URL"
echo "PROXY_PASSWORD=$PWD_SET"
echo "GOOGLE_API_KEY=$GAK_SET"
echo "-----------------"

docker build -t $scraper_name --no-cache .
rm -rf apify_docker_storage

docker run -e GOOGLE_API_KEY -e PROXY_URL -e PROXY_PASSWORD -e APIFY_LOCAL_STORAGE_DIR=apify_storage -e APIFY_TOKEN='' -v "${base_path}/apify_docker_storage:/apify_storage" $EXTRA_PARAMS ${scraper_name}:latest
