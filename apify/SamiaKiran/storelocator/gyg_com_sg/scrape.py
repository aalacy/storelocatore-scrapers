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
website = "gyg_com_sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.gyg.com.sg"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.gyg.com.sg/find-us"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "location w-dyn-item"})
        for loc in loclist:
            location_name = loc.find("h2").text
            if "Permanently closed" in location_name:
                continue
            temp = loc.findAll("div", {"class": "w-richtext"})
            raw_address = (
                temp[0].find("p").get_text(separator="|", strip=True).replace("|", " ")
            )
            phone = loc.find("div", {"class": "location-dd-content"}).find("p").text
            hours_of_operation = (
                temp[1]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .split("Public")[0]
            )
            latitude, longitude = loc.find(
                "div", {"class": "location__coordinates"}
            ).text.split(",")
            page_url = (
                DOMAIN + loc.find("a", string=re.compile("Visit Outlet Page"))["href"]
            )
            log.info(page_url)
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "SG"
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
                hours_of_operation=hours_of_operation,
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
