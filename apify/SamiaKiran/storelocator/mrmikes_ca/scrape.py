from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape import sgpostal as parser

session = SgRequests()
website = "mrmikes_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.mrmikes.ca/locations/"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.findAll("div", {"class": "storelocator__store"})
        for loc in loclist:
            page_url = loc["href"]
            r = session.get(page_url, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            temp = soup.find("div", {"class": "single-restaurant__general"}).findAll(
                "p"
            )
            raw_address = temp[0].text
            formatted_addr = parser.parse_address_intl(raw_address)
            street_address = formatted_addr.street_address_1
            if street_address is None:
                street_address = formatted_addr.street_address_2
            if formatted_addr.street_address_2:
                street_address = street_address + ", " + formatted_addr.street_address_2
            city = formatted_addr.city
            state = formatted_addr.state if formatted_addr.state else "<MISSING>"
            zip_postal = formatted_addr.postcode
            phone = temp[1].findAll("a")[1].text
            hour_list = soup.find("div", {"class": "single-restaurant__hours"}).findAll(
                "tr"
            )
            hours_of_operation = ""
            for hour in hour_list:
                hour = hour.findAll("td")
                time = hour[0].text
                day = hour[1].text
                hours_of_operation = hours_of_operation + " " + day + " " + time
            latitude = soup.find("input", {"class": "latitude"})["value"]
            longitude = soup.find("input", {"class": "longitude"})["value"]
            location_name = soup.find("h1").text.replace(" MR MIKES ", "")
            log.info(page_url)
            yield SgRecord(
                locator_domain="https://www.mrmikes.ca/",
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_postal,
                country_code="CA",
                store_number="<MISSING>",
                phone=phone,
                location_type="<MISSING>",
                latitude=latitude,
                longitude=longitude,
                hours_of_operation=hours_of_operation.strip(),
                raw_address=raw_address,
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
