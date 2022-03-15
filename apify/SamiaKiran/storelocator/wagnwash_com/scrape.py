import json
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "wagnwash_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://wagnwash.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    url = "https://wagnwash.com/locations"
    r = session.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    loclist = soup.findAll("p", {"class": "location-links"})
    for loc in loclist:
        page_url = loc.find("a")["href"]
        log.info(page_url)
        session_1 = SgRequests()
        r = session_1.get(page_url, headers=headers)
        temp = r.text.split("var locations = [ ")[1].split("}];", 1)[0]
        temp = temp + "}"
        temp = json.loads(temp)
        location_name = temp["name"]
        store_number = temp["id"]
        latitude = temp["latitude"]
        longitude = temp["longitude"]
        phone = temp["fran_phone"]
        try:
            street_address = (
                temp["fran_address"]
                + " "
                + temp["fran_address_2"].replace("&nbsp;", "")
            )
        except:
            street_address = temp["fran_address"].replace("&nbsp;", "")
        city = temp["fran_city"]
        state = temp["fran_state"]
        zip_postal = temp["fran_zip"]
        country_code = temp["fran_country"]
        hours_of_operation = temp["fran_hours"]
        location_type = MISSING
        soup = BeautifulSoup(hours_of_operation, "html.parser")
        hours_of_operation = (
            soup.find("p").get_text(separator="|", strip=True).split("|")
        )
        if hours_of_operation[0] == "COVID-19 Adjusted Hours":
            hours_of_operation = hours_of_operation[1] + " " + hours_of_operation[2]
        else:
            hours_of_operation = hours_of_operation[0] + " " + hours_of_operation[1]
        if "Grooming " in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Grooming", 1)[0]
        if "Curbside" in hours_of_operation:
            hours_of_operation = hours_of_operation.split("Curbside", 1)[0]
        if "COMING SOON!" in hours_of_operation:
            hours_of_operation = MISSING
            location_type = "COMING SOON"
        hours_of_operation = hours_of_operation.replace("Hours", "")
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=page_url,
            location_name=location_name.strip(),
            street_address=street_address.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=zip_postal.strip(),
            country_code=country_code,
            store_number=store_number,
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation.strip(),
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
