from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
import lxml.html
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
import json


session = SgRequests()
website = "sees_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "www.sees.com"
MISSING = SgRecord.MISSING


def fetch_data():
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
            location_name = location_details["name"]
            street_address = location_details["address"]["streetAddress"]
            city = location_details["address"]["addressLocality"]
            state = location_details["address"]["addressRegion"]
            zip = location_details["address"]["postalCode"]
            country_code = "US"
            if "-" in state:
                country_code = state.split("-")[0].strip()

            if state == "HK":
                country_code = "HK"

            store_number = "<MISSING>"
            phone = (
                location_details["address"]["telephone"]
                if location_details["address"]["telephone"]
                else "<MISSING>"
            )
            latitude = location_details["geo"]["latitude"]
            longitude = location_details["geo"]["longitude"]
            hours_of_operation = location_details["openingHours"]

            req = session.get(page_url, headers=headers)
            soup = BeautifulSoup(req.text, "lxml")
            isseasonal = soup.find("div", {"class": "seasonal"})
            try:
                isseasonal = isseasonal.text
                loc_type = isseasonal
            except AttributeError:
                if isseasonal is None:
                    loc_type = "Store"
            loc_type = loc_type.strip()
            if loc_type == "":
                loc_type = "Store"

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
                location_type=loc_type,
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
