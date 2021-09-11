from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json

website = "sees.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36"
    }
    with SgRequests() as session:
        r = session.get(
            "https://maps.sees.com/api/getAsyncLocations?template=search&level=search&radius=500000&search=11756",
            headers=headers,
        )
        data = r.json()["markers"]
        for store_data in data:
            store_soup = BeautifulSoup(store_data["info"], "lxml")
            page_url = json.loads(store_soup.find("div").text)["url"]
            log.info(page_url)
            location_request = session.get(page_url, headers=headers)
            location_sel = lxml.html.fromstring(location_request.text)

            location_details = json.loads(
                location_sel.xpath('//script[@type="application/ld+json"]/text()')[0]
            )[0]
            locator_domain = website
            location_name = location_details["name"]
            street_address = location_details["address"]["streetAddress"]
            city = location_details["address"]["addressLocality"]
            state = location_details["address"]["addressRegion"]
            zip = location_details["address"]["postalCode"]
            country_code = "US"
            store_number = "<MISSING>"
            phone = (
                location_details["address"]["telephone"]
                if location_details["address"]["telephone"]
                else "<MISSING>"
            )
            location_type = "<MISSING>"
            latitude = location_details["geo"]["latitude"]
            longitude = location_details["geo"]["longitude"]
            hours_of_operation = location_details["openingHours"]

            yield SgRecord(
                locator_domain=locator_domain,
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
