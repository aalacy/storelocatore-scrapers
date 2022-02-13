import json
import unicodedata
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


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


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
                location_name = strip_accents(loc["name"])
                log.info(location_name)
                store_number = loc["id"]
                phone = loc["phone"]
                street_address = strip_accents(loc["address1"])
                city = strip_accents(loc["city"])
                state = strip_accents(loc["state"])
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
