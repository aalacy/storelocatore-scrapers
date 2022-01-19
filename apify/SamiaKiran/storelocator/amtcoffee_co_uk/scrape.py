import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "amtcoffee_co_uk"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
}

DOMAIN = "https://amtcoffee.co.uk"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "http://amtcoffee.co.uk/locations/"
        r = session.get(url, headers=headers)
        loclist = r.text.split("pins: [{")[1].split("}],")[0]
        loclist = json.loads("[{" + loclist + "}]")
        for loc in loclist:
            location_name = loc["title"]
            store_number = loc["id"]
            phone = MISSING

            raw_address = location_name
            pa = parse_address_intl(raw_address)
            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING
            log.info(location_name)
            city = loc["city"]
            state = MISSING
            zip_postal = loc["zip"]
            if zip_postal.isalpha():
                zip_postal = MISSING
            soup = BeautifulSoup(loc["tooltipContent"], "html.parser")
            if len(soup.get_text(separator="|", strip=True).split("|")) == 1:
                hours_of_operation = MISSING
            else:
                hours_of_operation = (
                    soup.get_text(separator="|", strip=True)
                    .split("|")[1]
                    .replace("\r\n", " ")
                    .replace(
                        "(closed this weekend due to Irish Rail track upgrades )", ""
                    )
                    .replace("Open First to Last flight", "")
                )
                if "(closed" in hours_of_operation:
                    hours_of_operation = hours_of_operation.split("(closed")[0]
                if zip_postal in hours_of_operation:
                    hours_of_operation = (
                        soup.get_text(separator="|", strip=True)
                        .split("|")[2]
                        .replace("\r\n", " ")
                    )
            country_code = "UK"
            latitude, longitude = (
                str(loc["latlng"]).replace("[", "").replace("]", "").split(",")
            )
            raw_address = location_name + " " + city + " " + zip_postal
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url="https://www.rplumber.com/locations",
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
