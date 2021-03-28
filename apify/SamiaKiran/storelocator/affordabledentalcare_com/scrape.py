from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "affordabledentalcare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://www.affordabledentalcare.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", {"class": "uael-infobox-module-link"})
        for loc in loclist:
            page_url = loc["href"]
            location_name = (
                page_url.replace("https://www.affordabledentalcare.com/", "")
                .replace("/", "")
                .replace("-", " / ")
            )
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.findAll(
                "h4", {"class": "uael-infobox-title elementor-inline-editing"}
            )
            address = temp[0].get_text(separator="|", strip=True).split("|")
            street_address = address[0]
            address = address[1].split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = temp[1].text
            phone = soup.find(
                "h2", {"class": "uael-infobox-title elementor-inline-editing"}
            ).text
            coords = soup.find("iframe")["src"]
            r = session.get(coords, headers=headers)
            coords = (
                r.text.split('"Affordable Dental Care",null,[null,null,')[1]
                .split("],", 1)[0]
                .split(",")
            )
            latitude = coords[0]
            longitude = coords[1]
            yield SgRecord(
                locator_domain="https://www.affordabledentalcare.com/",
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
