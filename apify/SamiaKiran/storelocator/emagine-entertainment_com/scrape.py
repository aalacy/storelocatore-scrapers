from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup

website = "emagine-entertainment_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    if True:
        url = "https://www.emagine-entertainment.com/theatres/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "theatre-listings"}).findAll(
            "div", {"class": "theatre-listings__theatre"}
        )
        for loc in loclist:
            page_url = loc.find("a")["href"]
            r = session.get(page_url, headers=headers)
            log.info(page_url)
            soup = BeautifulSoup(r.text, "html.parser")
            try:
                store_number = r.text.split("full_address :")[1].split("title :", 1)[0]
                store_number = store_number.split('id : "')[1].split('",', 1)[0]
                location_name = soup.find("h1", {"class": "headline headline--1"}).text
                address = soup.findAll(
                    "p", {"class": "theatre-details__sidebar-group-item--address"}
                )
                street_address = address[0].text
                temp = address[1].text.split(",")
                city = temp[0]
                state = temp[1]
                try:
                    phone = (
                        soup.find(
                            "div", {"class": "theatre-details__sidebar-group sbgroup1"}
                        )
                        .find("a")
                        .text.strip()
                    )
                except:
                    phone = "<MISSING>"
            except:
                address = loc.find("div").get_text(separator="|", strip=True).split("|")
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                state = address[1]
                phone = "<MISSING>"
                store_number = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.emagine-entertainment.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal="<MISSING>",
                country_code="US",
                store_number=store_number.strip(),
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
                hours_of_operation="<MISSING>",
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
