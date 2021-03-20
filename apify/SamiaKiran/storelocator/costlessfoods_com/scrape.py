from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "costlessfoods.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://costlessfoods.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll(
            "div", {"class": "block block_content_photo bgcolor0 left padding_top"}
        )
        for loc in loclist:
            location_name = loc.find("div", {"class": "content_inner"}).find("h2").text
            temp = loc.find("div", {"class": "content_inner"}).findAll("p")
            phone = temp[0].findAll("strong")[1].text
            page_url = temp[1].find("a")["href"]
            page_url = "https://costlessfoods.com" + page_url
            log.info(page_url)
            address = temp[1].findAll("strong")
            street_address = address[0].text
            address = address[1].text.split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            hours_of_operation = temp[2].find("strong").text
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            latitude, longitude = (
                soup.find("div", {"class": "embed_container"})
                .find("iframe")["src"]
                .split("!1d", 1)[1]
                .split("!3d", 1)[0]
                .split("!2d")
            )
            latitude = latitude[2:]
            yield SgRecord(
                locator_domain="https://costlessfoods.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude.strip(),
                longitude=longitude.strip(),
                hours_of_operation=hours_of_operation,
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
