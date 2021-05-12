import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "hotboxpizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.hotboxpizza.com/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("a", href=re.compile("hotbox-pizza-locations"))[1:-1]
        for loc in loclist:
            page_url = loc["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                location_name = soup.find("h1", {"itemprop": "headline"}).text
            except:
                try:
                    location_name = soup.find("h2", {"itemprop": "headline"}).text
                except:
                    location_name = soup.find("h2").text
            try:
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
            except:
                longitude = "<MISSING>"
                latitude = "<MISSING>"
            try:
                temp_list = soup.findAll("div", {"itemprop": "text"})
                address = temp_list[1].get_text(separator="|", strip=True).split("|")
                street_address = address[0]
                hours_of_operation = " ".join(x for x in address[-2:])
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
            except:
                temp_list = soup.findAll("div", {"itemprop": "text"})
                address = temp_list[0].get_text(separator="|", strip=True).split("|")
                street_address = address[0]
                hours_of_operation = " ".join(x for x in address[-2:]).replace(
                    "Curbside and Delivery!", ""
                )
                address = address[1].split(",")
                city = address[0]
                address = address[1].split()
                state = address[0]
                zip_postal = address[1]
            phone = soup.select_one("a[href*=tel]").text
            yield SgRecord(
                locator_domain="https://www.hotboxpizza.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
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
