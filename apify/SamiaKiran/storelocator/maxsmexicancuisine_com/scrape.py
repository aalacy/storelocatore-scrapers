import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "maxsmexicancuisine_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.maxsmexicancuisine.com"
MISSING = SgRecord.MISSING


def parse_geo(url):
    lon = re.findall(r"\,(--?[\d\.]*)", url)[0]
    lat = re.findall(r"\@(-?[\d\.]*)", url)[0]
    return lat, lon


def fetch_data():
    if True:
        url = "https://www.maxsmexicancuisine.com/contact"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("footer").select("a[href*=maps]")
        r = session.get(DOMAIN, headers=headers)
        hours_of_operation = r.text.split("Monday")[1].split("Get In Touch")[0]
        hours_of_operation = "Monday " + BeautifulSoup(
            hours_of_operation, "html.parser"
        ).get_text(separator="|", strip=True).replace("|", " ")
        for loc in loclist:
            raw_address = loc.text
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            phone = r.text.split(city + ":")[1].split()
            phone = phone[0] + " " + phone[1]
            if "</span>" in phone:
                phone = phone.split("</span>")[0]
            coords = loc["href"]
            latitude, longitude = parse_geo(coords)
            country_code = "US"
            location_name = city + ", " + state
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
                location_type=MISSING,
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation,
                raw_address=raw_address,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
