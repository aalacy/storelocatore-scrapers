from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "sandhhealth_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "authority": "sandhhealth.com",
    "method": "GET",
    "path": "/pages/store-locator",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36",
}


def fetch_data():
    if True:
        url = "https://sandhhealth.com/pages/store-locator"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "card"})
        for loc in loclist:
            location_name = loc.find("h5").text.replace("\n", "").strip()
            log.info(location_name)
            try:
                temp = loc.find("div", {"class": "container"}).findAll(
                    "div", {"class": "col-sm"}
                )
                address = temp[0].get_text(separator="|", strip=True).split("|")[1:]
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].strip().split(" ", 1)
                state = address[0]
                zip_postal = address[1]
                hours_of_operation = (
                    temp[1].get_text(separator="|", strip=True).split("|")[1:]
                )
                hours_of_operation = " ".join(x for x in hours_of_operation)
                phone = temp[2].get_text(separator="|", strip=True).split("|")[1]
            except:
                temp = loc.find("div", {"class": "container"}).findAll(
                    "div", {"class": "col"}
                )
                address = temp[0].get_text(separator="|", strip=True).split("|")[1:]
                street_address = address[0]
                address = address[1].split(",")
                city = address[0]
                address = address[1].strip().split(" ", 1)
                state = address[0]
                zip_postal = address[1]
                hours_of_operation = (
                    temp[1].get_text(separator="|", strip=True).split("|")[1:]
                )
                hours_of_operation = " ".join(x for x in hours_of_operation)
                phone = temp[-1].get_text(separator="|", strip=True).split("|")[1]

            yield SgRecord(
                locator_domain="https://sandhhealth.com/",
                page_url="https://sandhhealth.com/pages/store-locator",
                location_name=location_name.strip(),
                street_address=street_address.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=zip_postal.strip(),
                country_code="CA",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude="<MISSING>",
                longitude="<MISSING>",
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
