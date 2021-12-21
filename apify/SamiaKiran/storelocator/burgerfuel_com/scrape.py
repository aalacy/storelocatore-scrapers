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
website = "burgerfuel_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)


headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


DOMAIN = "https://burgerfuel.com"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://burgerfuel.com/nz/locations"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = (
            soup.find("div", {"class": "content-inner"})
            .find("script")
            .text.replace(" var stores = {};", "")
            .split("['detailPageVisible'] = false;")
        )
        for loc in loclist[:-1]:
            page_url = DOMAIN + loc.split("['orderUrl'] = '")[1].split("'")[0]
            log.info(page_url)
            temp = json.loads("{" + loc.split("= {")[1].split("};")[0] + "}")
            location_name = temp["title"]
            store_number = temp["id"]
            coords = temp["coordinates"].replace("\xa0", "").split(",")
            longitude = coords[1]
            latitude = coords[0]
            phone = temp["phone"].split("-")[0]
            hours_of_operation = loc.split("['openingHours'] = '")[1].split("';")[0]
            hours_of_operation = (
                BeautifulSoup(hours_of_operation, "html.parser")
                .get_text(separator="|", strip=True)
                .replace("|", " ")
            )
            raw_address = temp["searchIndex"]
            if "life’s too short to eat bad burgers" in raw_address:
                raw_address = (
                    raw_address.split("life’s too short to eat bad burgers.")[1]
                    .replace("\r", "")
                    .strip()
                    .split("\n")[0]
                )
            pa = parse_address_intl(raw_address)

            street_address = pa.street_address_1
            street_address = street_address if street_address else MISSING

            city = pa.city
            city = city if city else MISSING

            state = pa.state
            state = state.strip() if state else MISSING

            zip_postal = pa.postcode
            zip_postal = zip_postal.strip() if zip_postal else MISSING
            if temp["regionId"] == "1":
                country_code = "NZ"
            elif temp["regionId"] == "3":
                country_code = "UAE"
            elif temp["regionId"] == "5":
                country_code = "SA"
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
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
