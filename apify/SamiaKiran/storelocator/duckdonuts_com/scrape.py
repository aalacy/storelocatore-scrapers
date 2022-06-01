from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


session = SgRequests()
website = "duckdonuts_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


headers = {
    "X-Requested-With": "XMLHttpRequest",
    "User-Agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1",
    "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
}

DOMAIN = "https://www.duckdonuts.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.duckdonuts.com/locations/?CallAjax=GetLocations"
        loclist = session.post(url, headers=headers).json()
        for loc in loclist:
            store_number = loc["FranchiseLocationID"]
            try:
                page_url = "https://www.duckdonuts.com" + loc["Path"]
            except:
                page_url = "https://www.duckdonuts.com/locations/"
            log.info(page_url)
            location_name = loc["FranchiseLocationName"]
            street_address = loc["Address1"]
            city = loc["City"]
            state = loc["State"]
            zip_postal = loc["ZipCode"]
            country_code = loc["Country"]
            phone = loc["Phone"]
            latitude = str(loc["Latitude"])
            longitude = str(loc["Longitude"])
            payload = (
                "_m_=HoursPopup&HoursPopup%24_edit_="
                + str(store_number)
                + "&HoursPopup%24_command_="
            )
            try:
                r = session.post(page_url, headers=headers, data=payload)
                soup = BeautifulSoup(r.text, "html.parser")
            except:
                continue
            hours_of_operation = (
                soup.find("table").get_text(separator="|", strip=True).replace("|", " ")
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
                location_type=MISSING,
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                hours_of_operation=hours_of_operation,
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
