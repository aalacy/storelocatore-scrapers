from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "katieskorner_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://katieskorner.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "http://katieskorner.com/StoreLocations.html"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("blockquote").findAll("td")
        for loc in loclist[3:]:
            loc = loc.get_text(separator="|", strip=True).split("|")
            if len(loc) == 1:
                continue
            location_name = (
                loc[0].replace("\n", " ").replace("                    ", " ")
            )
            log.info(location_name)
            street_address = loc[1]
            try:
                address = loc[2].split(",")
                city = address[0]
                state = address[1]
            except:
                address = loc[-1].split(",")
                city = address[0]
                state = address[1]
            zip_postal = MISSING
            country_code = "US"
            if len(loc) > 3:
                phone = loc[-1]
            else:
                phone = MISSING
            if "Beaver Falls" in location_name:
                phone = loc[-2]
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone.strip(),
                location_type=MISSING,
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=MISSING,
            )


def scrape():
    log.info("Started")
    count = 0
    with SgWriter() as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)
            count = count + 1

    log.info(f"No of records being processed: {count}")
    log.info("Finished")


if __name__ == "__main__":
    scrape()
