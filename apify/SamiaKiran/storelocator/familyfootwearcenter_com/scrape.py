from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter


website = "familyfootwearcenter_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.familyfootwearcenter.com/store-locations/shoe-stores"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "column3"}).findAll("a")
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "page-heading"}).text
            temp = soup.find("div", {"class": "page-content page-content--centered"})
            address = temp.get_text(separator="|", strip=True).split("|")
            phone = address[5]
            if "We encourage our customers" in address[7]:
                hours_of_operation = address[8] + " " + address[9]
            else:
                hours_of_operation = address[7] + " " + address[8]
            street_address = address[1]
            address = address[2].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            coords = soup.select_one("iframe[src*=maps]")["src"]
            r = session.get(coords, headers=headers)
            temp = "Family Footwear Center - " + city + "," + " " + state
            latitude, longitude = (
                r.text.split(temp, 2)[0]
                .rsplit('",', 1)[1]
                .split("]\\n")[0]
                .replace("[", "")
                .split(",")
            )
            yield SgRecord(
                locator_domain="https://www.familyfootwearcenter.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
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
