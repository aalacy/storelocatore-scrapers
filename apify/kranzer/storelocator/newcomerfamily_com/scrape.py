from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "newcomerfamily_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
}

DOMAIN = "https://www.newcomerfamily.com/"
MISSING = SgRecord.MISSING


def fetch_data():
    if True:
        url = "https://www.newcomerfamily.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        state_list = soup.findAll("ul", {"class": "dropdown-menu dropdown-menu-right"})[
            -2
        ].findAll("li")
        for temp_state in state_list:
            state_url = temp_state.find("a")["href"]
            log.info(f"Fetching locations from {temp_state.text}")
            r = session.get(state_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "chapel-text"})
            if not loclist:
                continue
            for loc in loclist:
                loc = loc.findAll("div", {"class": "row"})
                temp = loc[0].find("a")
                page_url = "https://www.newcomerdenver.com" + temp["href"]
                log.info(page_url)
                location_name = temp.text
                temp = loc[1].findAll("div")
                phone = loc[2].get_text(separator="|", strip=True).replace("|", "")
                try:
                    latitude, longitude = (
                        temp[0]
                        .find("a")["href"]
                        .split("sll=")[1]
                        .split("&sspn=")[0]
                        .split(",")
                    )
                except:
                    try:
                        coords = temp[0].find("a")["href"].split("@")[1].split(",")
                        latitude = coords[0]
                        longitude = coords[1]
                    except:
                        latitude = MISSING
                        longitude = MISSING
                address = temp[1].get_text(separator="|", strip=True).split("|")
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
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
                    store_number=MISSING,
                    phone=phone.strip(),
                    location_type=MISSING,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=MISSING,
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
