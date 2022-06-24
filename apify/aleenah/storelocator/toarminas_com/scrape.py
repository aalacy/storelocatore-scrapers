import json
from bs4 import BeautifulSoup
from sglogging import sglog
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "toarminas_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

DOMAIN = "https://toarminas.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    res = session.get("https://www.toarminas.com/locations/")
    soup = BeautifulSoup(res.text, "html.parser")
    state = (
        str(soup.find("script", {"id": "maplistko-js-extra"}))
        .split("var maplistScriptParamsKo =")[1]
        .split(";")[0]
    )
    loclist = json.loads(state)["KOObject"][0]["locations"]

    for loc in loclist:
        location_type = MISSING
        page_url = loc["locationUrl"]
        log.info(page_url)
        location_name = loc["title"]
        latitude = loc["latitude"]
        longitude = loc["longitude"]
        store_number = loc["cssClass"].split("loc-")[1]
        res = session.get(page_url)
        if "Coming Soon!" in res.text:
            continue
        if "Temporarily Closed" in res.text:
            location_type = "Temporarily Closed"
        temp = loc["description"]
        temp = (
            BeautifulSoup(temp, "html.parser")
            .get_text(separator="|", strip=True)
            .split("|")
        )
        phone = temp[-1].replace("P. ", "")
        location_name = loc["title"]
        if len(temp) > 4:
            if temp[0] == temp[2]:
                del temp[2]
                del temp[3]
        address = " ".join(temp[:-1])
        raw_address = (
            address.replace(",", " ")
            .replace("New Location!", "")
            .replace("United States", "")
        )
        pa = parse_address_intl(raw_address)

        street_address = pa.street_address_1
        street_address = street_address if street_address else MISSING

        city = pa.city
        city = city.strip() if city else MISSING

        state = pa.state
        state = state.strip() if state else MISSING

        zip_postal = pa.postcode
        zip_postal = zip_postal.strip() if zip_postal else MISSING
        res = session.get(page_url)
        soup = BeautifulSoup(res.text, "html.parser")
        hours_of_operation = (
            soup.findAll("div", {"class": "col-md-6"})[1]
            .get_text(separator="|", strip=True)
            .replace("|", " ")
        )
        if "Hours" not in hours_of_operation:
            hours_of_operation = MISSING
        else:
            hours_of_operation = hours_of_operation.split("Hours")[1]
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
            store_number=store_number,
            phone=phone.strip(),
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
            raw_address=raw_address,
        )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
