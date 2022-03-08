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
website = "macdonaldhotels_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.macdonaldhotels.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.macdonaldhotels.co.uk/our-hotels"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "destinationsCardRow__item"})
        for loc in loclist:
            page_url = DOMAIN + loc.find("a")["href"]
            if "resorts.macdonaldhotels.co.uk" in page_url:
                continue
            log.info(page_url)
            if "Spain" in loc.text:
                country_code = "SPAIN"
            else:
                country_code = "GB"
            r = session.get(page_url, headers=headers)
            try:
                soup = BeautifulSoup(r.text, "html.parser")
            except:
                continue
            try:
                location_name = (
                    soup.find(
                        "div", {"class": "heroBanner__title heroBanner__title--title"}
                    )
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
            except:
                location_name = soup.find("h1").text
            raw_address = (
                soup.find("div", {"class": "infoPanel__address"})
                .find("p")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("View on map", "")
            )
            try:
                phone = soup.find("div", {"class": "infoPanel__tel"}).find("a").text
            except:
                phone = MISSING
            try:
                hours_of_operation = soup.find("p", string=re.compile("Check")).text
            except:
                hours_of_operation = MISSING
            pa = parse_address_intl(raw_address.replace("View On Map", ""))

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING

            latitude = MISSING
            longitude = MISSING
            if zip_postal == MISSING:
                zip_postal = raw_address.split()
                zip_postal = zip_postal[-2] + " " + zip_postal[-1]
            street_address = street_address.lower().replace(zip_postal.lower(), "")
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
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
