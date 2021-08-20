from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "phohoa_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://phohoa.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://phohoa.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("tr", {"class": "striped"})
        loclist = loclist[: len(loclist) // 2]
        for loc in loclist:
            loc = loc.findAll("td")
            location_name = loc[0].text
            log.info(location_name)
            address = loc[1].get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            if len(address) > 2:
                state = address[0]
                zip_postal = address[1] + " " + address[2]
                country_code = "CA"
            else:
                state = address[0]
                zip_postal = address[1]
                country_code = "US"
            hours_of_operation = loc[2].text.replace("\n", " ")
            phone = loc[4].text
            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code=country_code,
                store_number=MISSING,
                phone=phone,
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
