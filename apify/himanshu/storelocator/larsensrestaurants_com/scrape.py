import json
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "larsensrestaurants_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
DOMAIN = "https://www.larsensrestaurants.com"
MISSING = SgRecord.MISSING


def fetch_data():

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "upgrade-insecure-request": "1",
    }

    url = "https://www.larsensrestaurants.com/locations-and-menus"
    r = session.get(url, headers=headers)
    base = BeautifulSoup(r.text, "lxml")
    items = base.find_all(class_="link-wrap")
    js = str(base.find(id="popmenu-apollo-state"))

    js_id = js.split("RestaurantLocation:")[1].split('"')[0]
    js_city = js.split('city":"')[1].split('"')[0]
    js_lat = js.split('lat":')[1].split(",")[0]
    js_lng = js.split('lng":')[1].split(",")[0]

    loclist = base.find_all("script", attrs={"type": "application/ld+json"})

    for loc in loclist:
        store = json.loads(loc.contents[0])

        street_address = store["address"]["streetAddress"]
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_postal = store["address"]["postalCode"]
        location_name = store["name"] + " - " + city
        country_code = "US"
        store_number = ""
        phone = store["telephone"]
        hours_of_operation = " ".join(store["openingHours"])
        location_type = ""
        latitude = ""
        longitude = ""
        for item in items:
            if city == js_city:
                store_number = js_id
                latitude = js_lat
                longitude = js_lng

            if city.lower() in item.text.lower():
                page_url = DOMAIN + item.a["href"].replace("..", "")

        log.info(page_url)
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
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
