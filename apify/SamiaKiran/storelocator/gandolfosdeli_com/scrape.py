from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


website = "gandolfosdeli_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://gandolfosdeli.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://gandolfosdeli.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.find("map", {"id": "usa_image_map"}).findAll("area")
        for state in state_list:
            state_url = state["href"]
            if state_url == "#":
                continue
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("li", {"class": "store-sub shslong"})
            for loc in loclist:
                page_url = loc.find("a")["href"]
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                location_name = soup.find("h2").text
                temp = soup.find("div", {"class": "store_content_right"})
                address = temp.findAll("h6")
                phone = address[1].find("img").text
                address = (
                    address[-1].find("a").get_text(separator="|", strip=True).split("|")
                )
                address_raw = " ".join(x for x in address[2:])
                pa = parse_address_intl(address_raw)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                hours_of_operation = soup.findAll("span", {"class": "storehours"})
                hours_of_operation = " ".join(
                    x.get_text(separator="|", strip=True).replace("|", " ")
                    for x in hours_of_operation
                )
                country_code = "US"
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
                    latitude=MISSING,
                    longitude=MISSING,
                    hours_of_operation=hours_of_operation.strip(),
                    raw_address=address_raw,
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
