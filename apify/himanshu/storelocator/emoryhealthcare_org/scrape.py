from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "emoryhealthcare.org"
BASE_URL = "https://www.emoryhealthcare.org"
LOCATION_URL = "https://www.emoryhealthcare.org/store-locator"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1985.125 Safari/537.36",
    "Host": "www.emoryhealthcare.org",
    "Origin": "https://www.emoryhealthcare.org",
    "Referer": "https://www.emoryhealthcare.org/locations/index.html?type=primary",
    "X-Requested-With": "XMLHttpRequest",
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}
MISSING = "<MISSING>"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests(verify_ssl=False)


def fetch_data():
    data = '{"selectFields":["Name","Address","City","State","Zip","URL","Type","Specialists","Latitude","Longitude"],"filters":{},"geoWithin":{},"orderBy":{"Name":-1}}'
    r = session.post(
        "https://www.emoryhealthcare.org/service/findPhysician/api/locations/retrieve",
        headers=HEADERS,
        data=data,
    )
    phone_request = session.get(
        "https://www.emoryhealthcare.org/locations/index.html?type=primary#map",
    )
    phone_soup = bs(phone_request.text, "lxml")
    phone = phone_soup.find("li", {"class": "hidden-xs"}).find_all("a")[-1].text
    data = r.json()["locations"]
    for row in data:
        page_url = BASE_URL + row["URL"].replace(" ", "") + ".html"
        location_name = row["NAME"]
        street_address = row["ADDRESS"]
        city = row["CITY"]
        state = row["STATE"]
        zip_postal = row["ZIP"]
        hours_of_operation = MISSING
        country_code = "US"
        store_number = MISSING
        location_type = row["Type"][0]
        latitude = row["LATITUDE"]
        longitude = row["LONGITUDE"]
        log.info(
            "Append {}: {} => {}".format(country_code, location_name, street_address)
        )
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
            phone=phone,
            location_type=location_type,
            latitude=latitude,
            longitude=longitude,
            hours_of_operation=hours_of_operation,
        )


def scrape():
    log.info("start {} Scraper".format(DOMAIN))
    count = 0
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LOCATION_NAME,
                    SgRecord.Headers.STREET_ADDRESS,
                }
            )
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1
    log.info(f"No of records being processed: {count}")
    log.info("Finished")


scrape()
