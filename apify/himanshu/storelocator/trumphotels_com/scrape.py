import json
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import cloudscraper

DOMAIN = "trumphotels.com"
BASE_URL = "https://www.trumphotels.com"
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36",
    "accept-encoding": "gzip, deflate, br",
}
MISSING = "<MISSING>"

log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()
session = cloudscraper.create_scraper(sess=session)


def get_latlng(map_link):
    if "z/data" in map_link:
        lat_lng = map_link.split("@")[1].split("z/data")[0]
        latitude = lat_lng.split(",")[0].strip()
        longitude = lat_lng.split(",")[1].strip()
    elif "ll=" in map_link:
        lat_lng = map_link.split("ll=")[1].split("&")[0]
        latitude = lat_lng.split(",")[0]
        longitude = lat_lng.split(",")[1]
    elif "!2d" in map_link and "!3d" in map_link:
        latitude = map_link.split("!3d")[1].strip().split("!")[0].strip()
        longitude = map_link.split("!2d")[1].strip().split("!")[0].strip()
    elif "/@" in map_link:
        latitude = map_link.split("/@")[1].split(",")[0].strip()
        longitude = map_link.split("/@")[1].split(",")[1].strip()
    else:
        latitude = "<MISSING>"
        longitude = "<MISSING>"
    return latitude, longitude


def fetch_data():
    if True:
        stores_req = session.get(BASE_URL)
        stores_sel = lxml.html.fromstring(stores_req.text)
        stores = stores_sel.xpath('//div[@class="filterlist"]//a/@href')
        for store_url in stores:
            page_url = BASE_URL + store_url
            log.info(page_url)
            store_req = session.get(page_url)
            store_sel = lxml.html.fromstring(store_req.text)
            json_list = store_sel.xpath('//script[@type="application/ld+json"]/text()')
            for js in json_list:
                store_data = json.loads(js)
                if "address" in store_data:
                    location_name = store_data["name"].replace("®", "")
                    address = store_data["address"]
                    if "streetAddress" not in address:
                        street_address = MISSING
                    else:
                        street_address = address["streetAddress"]
                    city = address["addressLocality"].split(",")[0]
                    state = (
                        address["addressRegion"].strip()
                        if "addressRegion" in address
                        else address["addressLocality"].split(",")[1]
                    )
                    if "postalCode" not in address:
                        street_address = MISSING
                    else:
                        zip = address["postalCode"]
                    country_code = (
                        "US"
                        if address["addressCountry"] == "USA"
                        else address["addressCountry"]
                    )
                    if "Aberdeenshire" in state:
                        country_code = "Scotland"
                    store_number = "<MISSING>"
                    phone = (
                        store_data["telephone"]
                        if store_data["telephone"]
                        else "<MISSING>"
                    )
                    location_type = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    map_link = store_sel.xpath(
                        '//a[contains(@href,"/maps/place")]/@href'
                    )
                    latitude, longitude = "<MISSING>", "<MISSING>"
                    if len(map_link) > 0:
                        map_link = map_link[0]

                        latitude, longitude = get_latlng(map_link)
                    log.info("Append {} => {}".format(location_name, street_address))
                    yield SgRecord(
                        locator_domain=DOMAIN,
                        page_url=page_url,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
