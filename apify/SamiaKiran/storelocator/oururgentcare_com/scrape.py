from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "oururgentcare_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.oururgentcare.com/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"id": "content-archive"}).findAll("article")
        for loc in loclist:
            store_number = loc["id"].replace("post-", "")
            page_url = loc.find("a")["href"]
            log.info(page_url)
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            location_name = soup.find("h1", {"class": "title"}).text
            street_address = soup.find("div", {"class": "address_1"}).text
            phone = soup.find("div", {"class": "phone_number"}).text
            hours_of_operation = soup.find("div", {"class": "hours"}).text
            address = soup.find("div", {"class": "address_2"}).text.split(",")
            city = address[0]
            address = address[1].split()
            state = address[0]
            zip_postal = address[1]
            latitude, longitude = (
                soup.find("a", {"id": "get-directions"})["href"]
                .split("addr=")[2]
                .split(",")
            )
            yield SgRecord(
                locator_domain="https://www.oururgentcare.com/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="US",
                store_number=store_number,
                phone=phone,
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
