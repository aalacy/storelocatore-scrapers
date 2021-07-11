from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "littlesprouts.com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://littlesprouts.com/schools/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        linklist = soup.findAll("div", {"class": "x-container max width"})
        for link in linklist:
            loclist = link.findAll("div", {"class": "x-column x-sm x-1-4"})
            for loc in loclist:
                try:
                    page_url = loc.find(
                        "a", {"class": "x-btn purple-btn x-btn-small x-btn-block"}
                    )["href"]
                except:
                    continue
                page_url = "https://littlesprouts.com" + page_url
                log.info(page_url)
                r = session.get(page_url, headers=headers, verify=False)
                soup = BeautifulSoup(r.text, "html.parser")
                longitude, latitude = (
                    soup.select_one("iframe[src*=maps]")["src"]
                    .split("!2d", 1)[1]
                    .split("!2m", 1)[0]
                    .split("!3d")
                )
                if "!3m" in latitude:
                    latitude = latitude.split("!3m")[0]
                location_name = soup.find("h1").text
                address = (
                    soup.select_one('p:contains("View Map")').text.split("|")[0].strip()
                )
                address = address.split(",")
                street_address = address[0]
                city = address[1]
                address = address[2].split()
                state = address[0]
                try:
                    zip_postal = address[1]
                except:
                    "<MISSING>"
                hours_of_operation = (
                    soup.select_one('h4:contains("Hours")')
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                phone = soup.select("a[href*=tel]")[1].text
                yield SgRecord(
                    locator_domain="https://littlesprouts.com/",
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
                    latitude=latitude,
                    longitude=longitude,
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
