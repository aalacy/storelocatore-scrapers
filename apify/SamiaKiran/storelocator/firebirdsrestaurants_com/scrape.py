from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_usa
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "firebirdsrestaurants_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://firebirdsrestaurants.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        r = session.get(DOMAIN, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("select", {"id": "select_your_location"}).findAll("option")
        for loc in loclist:
            page_url = loc["value"]
            log.info(page_url)
            if not page_url:
                continue
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1").text
            coords = (
                soup.find("a", {"class": "directions gtm_directions open_pixel"})[
                    "href"
                ]
                .split("&daddr=", 1)[1]
                .split(",")
            )
            latitude = coords[0]
            longitude = coords[1]
            address = soup.find("span", {"class": "addr"})
            temp = address.find("strong").text
            raw_address = address.text.replace(temp, "")
            if "Coming Soon" in raw_address:
                continue
            pa = parse_address_usa(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            country_code = "US"
            try:
                phone = soup.find("a", {"class": "body-tel gtm_phone_click"}).text
            except:
                phone = "<MISSING>"
            hourlist = soup.find("div", {"class": "hours-wrap"}).findAll("div")
            hours_of_operation = ""
            for hour in hourlist:
                day = hour.find("span", {"class": "day"}).text
                time = hour.find("span", {"class": "time"}).text
                hours_of_operation = hours_of_operation + day + " " + time + " "
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
