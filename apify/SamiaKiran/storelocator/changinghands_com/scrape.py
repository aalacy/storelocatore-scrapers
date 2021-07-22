from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "changinghands_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://changinghands.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://www.changinghands.com/page/contact-location-hours"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = (
            soup.find("div", {"class": "field-item even"})
            .findAll("div")[0]
            .findAll("div")
        )
        for loc in loclist:
            if len(loc) < 10:
                continue
            location_name = loc.find("h1").text
            loc = loc.findAll("div")
            address = loc[0].get_text(separator="|", strip=True).split("|")
            street_address = address[1]
            address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = (
                loc[1].find("p").get_text(separator="|", strip=True).split("|")
            )
            hours_of_operation = hours_of_operation[0] + " " + hours_of_operation[1]
            phone = loc[2].find("p").get_text(separator="|", strip=True).split("|")[3]
            page_url = loc[3].find("a")["href"]
            log.info(page_url)
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
                latitude=MISSING,
                longitude=MISSING,
                hours_of_operation=hours_of_operation.strip(),
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
