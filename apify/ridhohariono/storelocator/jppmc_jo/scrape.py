from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
from sglogging import sglog
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

DOMAIN = "jppmc.jo"
LOCATION_URL = "http://www.jppmc.jo/Pages/viewpage.aspx?pageID=78"
HEADERS = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36",
}
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)

session = SgRequests()


MISSING = "<MISSING>"


def pull_content(url):
    log.info("Pull content => " + url)
    HEADERS["Referer"] = url
    soup = bs(session.get(url, headers=HEADERS).content, "lxml")
    return soup


def fetch_data():
    log.info("Fetching store_locator data")
    soup = pull_content(LOCATION_URL)
    contents = soup.select("div.divList div.divBlock")
    for row in contents:
        location_name = row.find("span", {"class": "lblName1"}).text.strip()
        info = row.find("a", {"class": "btnMap"})
        if not info:
            info = row.find_all("span", {"class": "lblBrief"})
            street_address = info[1].text.strip()
            phone = info[0].text.strip()
            latitude = MISSING
            longitude = MISSING
        else:
            street_address = info["data-address"]
            phone = info["data-phone"]
            latitude = info["data-lat"].split(",")[0]
            longitude = info["data-lng"].split(",")[0]
        street_city = street_address.split("-")
        if len(street_city) > 1:
            city = street_city[0]
        else:
            city = MISSING
        state = MISSING
        zip_postal = MISSING
        country_code = "JO"
        store_number = MISSING
        hours_of_operation = MISSING
        location_type = MISSING
        log.info("Append {} => {}".format(location_name, street_address))
        yield SgRecord(
            locator_domain=DOMAIN,
            page_url=LOCATION_URL,
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
            raw_address=street_address,
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
