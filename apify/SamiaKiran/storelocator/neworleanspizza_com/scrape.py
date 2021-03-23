from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests import SgRequests
from sglogging import sglog
from bs4 import BeautifulSoup
from sgscrape import sgpostal as parser

website = "neworleanspizza_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    temp = []
    if True:
        url = "https://www.neworleanspizza.com/locations.aspx"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        temp_city = soup.find("select", {"id": "city"}).findAll("option")[1]["value"]
        link = (
            "https://www.neworleanspizza.com/locations.aspx?address=&city="
            + temp_city
            + "&Countryui=&pageNumber=1"
        )
        r = session.get(link, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        no_of_pages = soup.find("div", {"class": "page"}).findAll("a")
        i = 1
        for page in no_of_pages:
            link = (
                "https://www.neworleanspizza.com/locations.aspx?address=&city="
                + temp_city
                + "&Countryui=&pageNumber="
                + str(i)
            )
            r = session.get(link, headers=headers)
            soup = BeautifulSoup(r.text, "html.parser")
            loclist = soup.findAll("div", {"class": "location-list"})
            i = i + 1
            for loc in loclist:
                page_url = loc.findAll("a")[1]["href"]
                page_url = "https://www.neworleanspizza.com/" + page_url
                log.info(page_url)
                r = session.get(page_url, headers=headers)
                soup = BeautifulSoup(r.text, "html.parser")
                raw_address = (
                    soup.find("div", {"class": "location-detail"})
                    .find("p")
                    .text.replace("TEMPORARILY CLOSED ", "")
                    .replace("\n", " ")
                )
                formatted_addr = parser.parse_address_intl(raw_address)
                street_address = formatted_addr.street_address_1
                if street_address is None:
                    street_address = formatted_addr.street_address_2
                if formatted_addr.street_address_2:
                    street_address = (
                        street_address + ", " + formatted_addr.street_address_2
                    )
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zip_postal = formatted_addr.postcode
                country_code = "CA"
                phone = soup.select_one("a[href*=tel]").text.replace("CALL ", "")
                location_name = (
                    soup.find("div", {"class": "location-detail"}).find("h1").text
                )
                hours_of_operation = (
                    soup.find("div", {"class": "hours"})
                    .findAll("p")[1]
                    .get_text(separator="|", strip=True)
                    .replace("|", " ")
                )
                temp = r.text.split("var locations = [",)[1].split(
                    "}", 1
                )[0]
                latitude = temp.split("lat: eval(")[1].split(")", 1)[0]
                longitude = temp.split("lng: eval(")[1].split(")", 1)[0]
                store_number = temp.split("storeNumber: '")[1].split("'", 1)[0]
                yield SgRecord(
                    locator_domain="https://www.neworleanspizza.com/",
                    page_url=page_url,
                    location_name=location_name.strip(),
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_postal,
                    country_code=country_code,
                    store_number=store_number.strip(),
                    phone=phone.strip(),
                    location_type="<MISSING>",
                    latitude=latitude.strip(),
                    longitude=longitude.strip(),
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
