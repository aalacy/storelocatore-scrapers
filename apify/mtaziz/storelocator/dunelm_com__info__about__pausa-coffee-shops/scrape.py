from sglogging import SgLogSetup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
import ssl
import json


try:
    _create_unverified_https_context = (
        ssl._create_unverified_context
    )  # Legacy Python that doesn't verify HTTPS certificates by default
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context  # Handle target environment that doesn't support HTTPS verification

DOMAIN = "dunelm.com/info/about/pausa-coffee-shops"
MISSING = SgRecord.MISSING
logger = SgLogSetup().get_logger("dunelm_com__info__about__pausa-coffee-shops")
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
}

MAX_WORKERS = 10


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_post(api_url, payload, headers_p):
    with SgRequests() as http:
        r1 = http.post(api_url, data=json.dumps(payload), headers=headers_p)
        if r1.status_code == 200:
            logger.info(f"HTTP Status Code: {r1.status_code}")
            return r1
        raise Exception(f"{api_url} | {payload} >> HTTPCodeError: {r1.status_code}")


def get_hoo(htest):
    hours = []
    date_map = [
        "Sunday",
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
    ]
    for i in htest:
        date = ""
        if i["day"] == 0:
            date = f"{date_map[0]} {i['open']} - {i['close']}"
            hours.append(date)
        elif i["day"] == 1:
            date = f"{date_map[1]} {i['open']} - {i['close']}"
            hours.append(date)
        elif i["day"] == 2:
            date = f"{date_map[2]} {i['open']} - {i['close']}"
            hours.append(date)
        elif i["day"] == 3:
            date = f"{date_map[3]} {i['open']} - {i['close']}"
            hours.append(date)
        elif i["day"] == 4:
            date = f"{date_map[4]} {i['open']} - {i['close']}"
            hours.append(date)
        elif i["day"] == 5:
            date = f"{date_map[5]} {i['open']} - {i['close']}"
            hours.append(date)

        elif i["day"] == 6:
            date = f"{date_map[6]} {i['open']} - {i['close']}"
            hours.append(date)
        else:
            pass
    return hours


def fetch_records(snum, store_uri, sgw: SgWriter):
    try:
        API_ENDPOINT_URL = "https://was.dunelm.com/graphql"
        payload = {
            "query": "query StoreById($id: String!) {\n  storeById(input: {id: $id}) {\n    ...storeAttributes\n    clickAndCollect\n    facilities {\n      facility\n      facilityIcon\n    }\n  }\n}\n\nfragment storeAttributes on Store {\n  sapSiteId\n  name\n  uri\n  streetAddress\n  localArea\n  city\n  county\n  postcode\n  country\n  phone\n  location {\n    lat\n    lon\n  }\n  tillTimes\n  openingHours {\n    day\n    open\n    close\n  }\n  seoText {\n    type\n    text\n    spans {\n      start\n      end\n      type\n    }\n  }\n}\n",
            "variables": {"id": store_uri},
        }

        r = get_response_post(API_ENDPOINT_URL, payload, headers)
        son = r.json()
        store_by_id = son["data"]["storeById"]
        for j in store_by_id:

            location_name = j["name"] or MISSING

            # Page URL
            suri = j["uri"]
            store_locator_url = "https://www.dunelm.com/stores/"
            page_url = f"{store_locator_url}{suri}"
            logger.info(f"Crawled: [{snum}] [{suri}] [ {page_url} ]")  # noqa

            sta = ""
            sta1 = j["streetAddress"]
            sta2 = j["localArea"]
            if sta1 and sta2:
                sta = sta1 + ", " + sta2
            elif sta1 and not sta2:
                sta = sta1
            elif not sta1 and sta2:
                sta = sta2
            else:
                sta = MISSING
            city = j["city"] or MISSING
            state = j["county"] or MISSING
            zip_postal = j["postcode"] or MISSING
            country_code = j["country"] or MISSING
            store_number = j["sapSiteId"] or MISSING
            phone = j["phone"] or MISSING
            lat = j["location"]["lat"] or MISSING
            lng = j["location"]["lon"] or MISSING
            htest = j["openingHours"]
            hoo = ""
            try:
                hoo = get_hoo(htest)
                hoo = "; ".join(hoo)
            except:
                hoo = MISSING

            location_type = ""
            try:
                facilities = [i["facility"] for i in j["facilities"]]
                location_type = "; ".join(facilities)
            except:
                location_type = MISSING

            item = SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=sta,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number=store_number,
                phone=phone,
                location_type=location_type,
                latitude=lat,
                longitude=lng,
                hours_of_operation=hoo,
                raw_address=MISSING,
            )

            sgw.write_row(item)
    except Exception as e:
        logger.info(f"Fix FetchRecordsError: << {e} >> at [{snum}] [{store_uri}]")


def get_uri_list():
    api_url_az = "https://fy8plebn34-1.algolianet.com/1/indexes/*/queries?x-algolia-agent=Algolia%20for%20JavaScript%20(3.35.1)%3B%20Browser%3B%20JS%20Helper%20(3.4.4)%3B%20react%20(17.0.2)%3B%20react-instantsearch%20(6.10.3)&x-algolia-application-id=FY8PLEBN34&x-algolia-api-key=ae9bc9ca475f6c3d7579016da0305a33"
    payload_az = {
        "requests": [
            {
                "indexName": "stores_prod",
                "params": "highlightPreTag=%3Cais-highlight-0000000000%3E&highlightPostTag=%3C%2Fais-highlight-0000000000%3E&page=0&hitsPerPage=1000&attributesToRetrieve=%5B%22storeName%22%2C%22uri%22%5D&facets=%5B%5D&tagFilters=",
            }
        ]
    }
    r_az = get_response_post(api_url_az, payload_az, headers)
    son_az = r_az.json()
    results_store_names = son_az["results"]
    results_hits = results_store_names[0]["hits"]
    uri_list = [i["uri"] for i in results_hits]
    uri_list = sorted(uri_list)
    return uri_list


def fetch_data(sgw: SgWriter):
    logger.info("Crawling stores URI")
    store_names = get_uri_list()
    logger.info(f"Stores URI crawling Done!! Total Stores: {len(store_names)} ")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, snum, storename, sgw)
            for snum, storename in enumerate(store_names[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            if future.result() is not None:
                future.result()
            else:
                continue


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
