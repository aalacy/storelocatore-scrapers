from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "guzmanygomez_com_au"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.guzmanygomez.com.au"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.guzmanygomez.com.au/all-locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.select("a[href*=all-location]")
        for loc in loclist:
            location_type = MISSING
            page_url = loc["href"]
            closed = loc.text.split(" - ")
            closed = closed[-1]
            if (
                closed == "TEMP CLOSED"
                or closed == "TEMPORARILY CLOSED"
                or closed == "CLOSED"
            ):
                location_type = "TEMPORARILY CLOSED"
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = (
                soup.find("h2")
                .get_text(separator="|", strip=True)
                .replace("|", "")
                .split("–")[0]
            )
            log.info(location_name)
            raw_address = soup.find("div", {"class": "order_location"})
            address = raw_address.findAll("span")
            raw_address = raw_address.get_text(separator="|", strip=True).replace(
                "|", " "
            )
            street_address = address[-4].text
            city = address[-3].text
            state = address[-2].text
            zip_postal = address[-1].text
            temp = soup.findAll("table", {"class": "order_location"})
            try:
                hours_of_operation = (
                    temp[1].get_text(separator="|", strip=True).replace("|", " ")
                )
            except:
                hours_of_operation = MISSING
            if hours_of_operation == "Temporarily Closed":
                hours_of_operation = MISSING
                location_type = "TEMPORARILY CLOSED"
            elif "TEMP: CLOSED Mon" in hours_of_operation:
                hours_of_operation = hours_of_operation.replace("TEMP: CLOSED", "")
                location_type = "TEMPORARILY CLOSED"
            elif hours_of_operation == "TEMP: CLOSED":
                hours_of_operation = MISSING
                location_type = "TEMPORARILY CLOSED"
            phone = (
                temp[0]
                .findAll("td")[1]
                .get_text(separator="|", strip=True)
                .replace("|", "")
            )
            if "26/09/21: 11:30 - 21:30" in hours_of_operation:
                hours_of_operation = hours_of_operation.split(
                    "26/09/21: 11:30 - 21:30"
                )[1]
            country_code = "AUS"
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
                location_type=location_type,
                latitude=MISSING,
                longitude=MISSING,
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
