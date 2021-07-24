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
website = "patrickmorin_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://patrickmorin.com/"
MISSING = "<MISSING>"


def strip_accents(text):

    text = unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

    return str(text)


def fetch_data():
    url = "https://www.patrickmorin.com/fr/magasins"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = r.text.split('"markers":')[1].split(',"type"')[0]
    loclist = json.loads(loclist)
    for loc in loclist:
        page_url = loc["url"]
        store_number = loc["id"]
        location_name = loc["name"]
        location_name = strip_accents(location_name)
        log.info(page_url)
        r = session.get(page_url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp = soup.find("div", {"class": "footer-block store-contact-info"})
        phone = temp.find("p", {"class": "store-phone-number"}).find("a").text
        hours_of_operation = temp.findAll("p")[-3].text
        address = (
            soup.find("div", {"class": "address"})
            .find("span")
            .get_text(separator="|", strip=True)
            .split("|")
        )
        street_address = address[0]
        address = address[1].split(",")
        city = address[0]
        state = address[1]
        street_address = strip_accents(street_address)
        city = strip_accents(city)
        state = strip_accents(state)
        zip_postal = address[2]
        country_code = "CA"
        latitude = soup.find("meta", {"itemprop": "latitude"})["content"]
        longitude = soup.find("meta", {"itemprop": "longitude"})["content"]
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
            location_type=MISSING,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
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
