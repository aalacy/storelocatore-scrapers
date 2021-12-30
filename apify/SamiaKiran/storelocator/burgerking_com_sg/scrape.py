from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "burgerking_com_sg"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://burgerking.com.sg/Locator"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        for link in range(1, 50):
            url = "https://burgerking.com.sg/Locator?page=" + str(link)
            log.info(f"Page No {link}")
            main_r = session.get(url, headers=headers)
            soup = BeautifulSoup(main_r.text, "html.parser")
            loclist = soup.find("div", {"id": "locationsList"}).findAll(
                "div", {"class": "location"}
            )
            for loc in loclist:
                page_url = (
                    "https://burgerking.com.sg"
                    + loc.find("a", {"class": "link more-info"})["href"]
                )
                store_number = loc["data-restaurant-id"]
                location_name = loc.find("dt", {"class": "mainAddress"}).text
                hour_list = (
                    loc.find("dd", {"class": "store-hours"}).find("tbody").findAll("tr")
                )
                hours_of_operation = ""
                for hour in hour_list[:-2]:
                    hour = hour.findAll("td")
                    hours_of_operation = (
                        hours_of_operation + " " + hour[0].text + " " + hour[1].text
                    )
                latitude = MISSING
                longitude = MISSING
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                phone = soup.find("strong", {"itemprop": "telephone"}).text
                raw_address = soup.find(
                    "span", {"itemprop": "streetAddress"}
                ).text.replace("\n", "")
                pa = parse_address_intl(raw_address)
                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING
                city = pa.city
                city = city.strip() if city else MISSING
                state = pa.state
                state = state.strip() if state else MISSING
                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = pa.country
                country_code = country_code.strip() if country_code else MISSING
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
                    hours_of_operation=hours_of_operation,
                    raw_address=raw_address,
                )
            if "Next" not in main_r.text:
                break


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
