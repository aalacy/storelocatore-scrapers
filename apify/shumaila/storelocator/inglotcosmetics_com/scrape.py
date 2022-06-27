import json
import unicodedata
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "inglotcosmetics_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://inglotcosmetics.com/"
MISSING = SgRecord.MISSING


def strip_accents(text):
    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")
    return str(text)


def fetch_data():
    url = "https://inglotcosmetics.com/index.php?option=com_ajax&plugin=istorelocator&tmpl=component&format=json&lat=0&lng=0&maxdistance=123456&limit=123456&source=com_contactenhanced&file=&category=12"
    loclist = session.get(url, headers=headers).json()["data"][0]["list"]
    soup = BeautifulSoup(str(loclist), "html.parser")
    divlist = soup.findAll("li")
    for div in divlist:
        content = json.loads(div["data-gmapping"])
        latitude = content["lat"]
        longitude = content["lng"]
        store_number = content["id"]
        country_code = div.find("span", {"class": "loc-country"}).text
        location_name = strip_accents(div.find("div", {"class": "loc-name"}).text)
        log.info(location_name)
        try:
            street_address = strip_accents(
                div.find("span", {"class": "loc-address"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            pass
        try:
            city = strip_accents(
                div.find("span", {"class": "loc-city"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            pass
        try:
            zip_postal = strip_accents(
                div.find("span", {"class": "loc-postcode"})
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
        except:
            pass
        raw_address = (
            street_address.strip() + " " + city.strip() + " " + zip_postal.strip()
        )
        raw_address = raw_address.replace(",", " ")
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url="https://inglotcosmetics.com/stores",
            location_name=location_name,
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=MISSING,
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=MISSING,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
