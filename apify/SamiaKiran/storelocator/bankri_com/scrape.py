from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "bankri_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

DOMAIN = "https://bankri.com/"
MISSING = "<MISSING>"


def fetch_data():
    if True:
        url = "https://bankri.com/locations/"
        r = session.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "location-results"}).findAll("a")
        for loc in loclist:
            page_url = "https://bankri.com/" + loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h2").text
            address = (
                soup.findAll("td", {"class": "tablecontent1"})[1]
                .get_text(separator="|", strip=True)
                .split("|")
            )
            phone = address[2]
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            country_code = "US"
            hours_of_operation = " ".join(
                x.text.replace("\n", " ")
                for x in soup.findAll("table")[1].findAll("tr")[1:]
            )
            if not hours_of_operation:
                hours_of_operation = " ".join(
                    x.text.replace("\n", " ")
                    for x in soup.findAll("table")[2].findAll("tr")[1:]
                )

            yield SgRecord(
                locator_domain=DOMAIN,
                page_url=page_url,
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
