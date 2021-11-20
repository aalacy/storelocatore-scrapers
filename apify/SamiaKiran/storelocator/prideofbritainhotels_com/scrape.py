from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "prideofbritainhotels_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}


DOMAIN = "https://www.prideofbritainhotels.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.prideofbritainhotels.com/map/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("var hotels = [")[1].split("];")[0].split("]],")[:-1]
        for loc in loclist:
            loc = loc.strip().split(",  [")[0].split("[")[1].split(", '")
            temp = loc[0].split("',")
            location_name = temp[0].replace("'", "")
            latitude, longitude = temp[1].split(",")
            page_url = loc[-2].strip().replace("'", "").strip()
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find(
                "div", {"class": "hotel-contact hotel-centered hotel-section"}
            ).findAll("div", {"class": "hotel-row"})
            raw_address = (
                temp[0]
                .get_text(separator="|", strip=True)
                .replace("|", " ")
                .replace("Address", "")
            )
            hours_of_operation = soup.find("div", {"class": "hotel-need hotel-section"})
            if hours_of_operation is None:
                hours_of_operation = MISSING
            else:
                hours_of_operation = hours_of_operation.findAll(
                    "div", {"class": "hotel-row"}
                )
                if len(hours_of_operation) == 1:
                    hours_of_operation = MISSING
                else:
                    open_time = hours_of_operation[0].text

                    if "Number" in open_time:
                        open_time = hours_of_operation[1]
                        close_time = hours_of_operation[2]
                    else:
                        open_time = hours_of_operation[0]
                        close_time = hours_of_operation[1]
                    hours_of_operation = (
                        open_time.find("div", {"class": "right"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                        + " - "
                        + close_time.find("div", {"class": "right"})
                        .get_text(separator="|", strip=True)
                        .replace("|", " ")
                    )
                    hours_of_operation = (
                        hours_of_operation.replace("Check-out at", "")
                        .replace("Check-in at", "")
                        .replace("Check-out is", "")
                        .replace("Check-in is", "")
                        .replace("Check-out at", "")
                        .replace("Check-out", "")
                        .replace("Check out by", "")
                        .replace("Check in from", "")
                        .replace("Check out at", "")
                        .replace("at", "")
                        .replace(
                            " (guests can arrive early to enjoy the hotel facilities)",
                            "",
                        )
                    ).strip("-")
            if "Boarding from" in hours_of_operation:
                hours_of_operation = MISSING
            if "Lee Clarke" in hours_of_operation:
                hours_of_operation = hours_of_operation.split("Lee Clarke ")[0]
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city.strip() if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            phone = temp[2].select_one("a[href*=tel]").text
            country_code = "UK"
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
