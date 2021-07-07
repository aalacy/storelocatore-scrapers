from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgpostal import parse_address_intl

website = "chamberlins_com"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}

MISSING = "<MISSING>"


def fetch_data():
    temp = []
    if True:
        url = "https://chamberlins.com/locations/"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        divlist = soup.find("div", {"class": "container"}).findAll(
            "div", {"class": "row"}
        )[1:]
        for div in divlist:
            loclist = div.findAll("div", {"class": "col-md-6"})
            for loc in loclist:
                temp = loc.find("div", {"class": "locationAddress"}).findAll("p")
                location_name = temp[0].text
                log.info(location_name)
                location_type = MISSING
                try:
                    temp_1 = temp[2].get_text(separator="|", strip=True).split("|")
                    phone = temp_1[-3].split("Phone:", 1)[1]
                    hours_of_operation = temp_1[-2] + " " + temp_1[-1]
                    address = " ".join(
                        temp[1].get_text(separator="|", strip=True).split("|")
                    )
                except:
                    if "Summer 2021" in temp[1].text:
                        location_type = "Coming Soon"
                    temp_1 = temp[3].get_text(separator="|", strip=True).split("|")
                    phone = temp_1[-3].split("Phone:", 1)[1]
                    hours_of_operation = temp_1[-2] + " " + temp_1[-1]
                    address = " ".join(
                        temp[2].get_text(separator="|", strip=True).split("|")
                    )
                try:
                    coords = (
                        loc.find("div", {"class": "directionsStyles"})
                        .find("a")["href"]
                        .split("@", 1)[1]
                        .split(",")
                    )
                    latitude = coords[0]
                    longitude = coords[1]
                except:
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                # Parse the address
                pa = parse_address_intl(address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
                country_code = "US"

                yield SgRecord(
                    locator_domain="https://chamberlins.com/",
                    page_url="https://chamberlins.com/locations/",
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code=country_code,
                    store_number=MISSING,
                    phone=phone,
                    location_type=location_type,
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
