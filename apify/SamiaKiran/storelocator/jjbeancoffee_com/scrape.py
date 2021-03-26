from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "jjbeancoffee_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://jjbeancoffee.com/pages/locations"
        r = session.get(url, headers=headers).json()["page"]["body_html"]
        soup = BeautifulSoup(r, "html.parser")
        loclist = soup.findAll("div", {"style": "text-align: left;"})
        for loc in loclist:
            location_name = loc.find("a").text
            log.info(location_name)
            temp_list = loc.findAll("p")
            try:
                coords = temp_list[0].find("a")["href"].split("/")[6].split(",")
                latitude = coords[0].replace("@", "")
                longitude = coords[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"
            hours_of_operation = temp_list[1].text
            phone = temp_list[2].text.split("|")[1].replace("Phone:", "")
            address = temp_list[0].find("a").text.split(",")
            street_address = address[0]
            city = address[1]
            state = "<MISSING>"
            zip_postal = "<MISSING>"
            country_code = "CA"
            page_url = "https://jjbeancoffee.com/pages/locations"
            yield SgRecord(
                locator_domain="https://jjbeancoffee.com/",
                page_url=page_url,
                location_name=location_name.strip(),
                street_address=street_address,
                city=city.strip(),
                state=state,
                zip_postal=zip_postal,
                country_code=country_code,
                store_number="<MISSING>",
                phone=phone.strip(),
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
