import json
import html
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "parfois_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.parfois.com/pt/ao/home/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.parfois.com/on/demandware.store/Sites-Parfois_South_Europe-Site/en_US/Stores-FindStoresState"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        country_list = soup.findAll("link", {"rel": "alternate"})[1:]
        for country in country_list:
            country_url = country["href"]
            r = session.get(country_url, headers=headers)
            country_code = country_url.split("/")[-2].split("_")[1]
            log.info(f"Fetching locations from {country_code}.........")
            loclist = r.text.split("markersData.push(")[1:]
            for loc in loclist:
                loc = json.loads(loc.split(");")[0])
                location_name = html.unescape(loc["name"])
                log.info(location_name)
                store_number = loc["id"]
                phone = html.unescape(loc["phone"])
                street_address = html.unescape(loc["address1"])
                city = html.unescape(loc["city"])
                state = html.unescape(loc["state"])
                zip_postal = loc["postalCode"]
                latitude = loc["latitude"]
                longitude = loc["longitude"]
                hours_of_operation = MISSING
                if "null" in phone:
                    phone = MISSING
                if "null" in state:
                    state = MISSING
                if "0" in zip_postal:
                    zip_postal = MISSING
                if "null" in zip_postal:
                    zip_postal = MISSING
                if "null" in latitude:
                    latitude = MISSING
                if "null" in longitude:
                    longitude = MISSING
                if len(zip_postal) < 3:
                    zip_postal = MISSING
                raw_address = (
                    street_address + " " + city + " " + state + " " + zip_postal
                )
                raw_address = raw_address.replace(MISSING, "")
                raw_address = html.unescape(raw_address)
                yield SgRecord(
                    locator_domain=DOMAIN,
                    page_url=country_url,
                    location_name=location_name,
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=raw_address,
                )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
