import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape import sgpostal as parser
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter

session = SgRequests()
website = "pumpernickels_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
    "Accept": "application/json",
}


def fetch_data():
    if True:
        url = "https://www.pumpernickels.ca/location"
        r = session.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "location-custom-div"}).findAll("p")[6:-1]
        for loc in loclist:
            coords = loc.findAll("u")
            if len(coords) > 1:
                temp_list = loc.get_text(separator="|", strip=True).split("DIRECTIONS")[
                    :-1
                ]
                for temp, coord in zip(temp_list, coords):
                    latitude, longitude = re.findall(
                        r"/@(-?[\d\.]+),(-?[\d\.]+)", coord.find("a")["href"]
                    )[0]
                    temp = temp.strip("|").split("|")
                    if re.match(
                        r"^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$",
                        temp[-2].replace(" (Catering)", ""),
                    ):
                        phone = temp[-2].replace(" (Catering)", "")
                        hours_of_operation = temp[-1]
                        raw_address = " ".join(x for x in temp[1:-2])
                    else:
                        phone = temp[-3].replace(" (Catering)", "")
                        raw_address = " ".join(x for x in temp[1:-3])
                        hours_of_operation = " ".join(x for x in temp[-2:])
                    location_name = temp[0]
                    log.info(location_name)
                    formatted_addr = parser.parse_address_intl(raw_address)
                    street_address = formatted_addr.street_address_1
                    if street_address is None:
                        street_address = formatted_addr.street_address_2
                    if formatted_addr.street_address_2:
                        street_address = (
                            street_address + ", " + formatted_addr.street_address_2
                        )
                    city = formatted_addr.city
                    state = (
                        formatted_addr.state if formatted_addr.state else "<MISSING>"
                    )
                    zip_postal = formatted_addr.postcode
                    yield SgRecord(
                        locator_domain="https://www.pumpernickels.ca/",
                        page_url="https://www.pumpernickels.ca/location",
                        location_name=location_name.strip(),
                        street_address=street_address.strip(),
                        city=city.strip(),
                        state=state.strip(),
                        zip_postal=zip_postal.strip(),
                        country_code="CAN",
                        store_number="<MISSING>",
                        phone=phone,
                        location_type="<MISSING>",
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                    )

            else:
                latitude, longitude = re.findall(
                    r"/@(-?[\d\.]+),(-?[\d\.]+)", coords[0].find("a")["href"]
                )[0]
                temp = loc.get_text(separator="|", strip=True).split("|")[:-1]
                temp_phone = temp[-2].replace(" (Catering)", "").replace(" X 1", "")
                if re.match(
                    r"^(\([0-9]{3}\) |[0-9]{3}-)[0-9]{3}-[0-9]{4}$", temp_phone
                ):
                    phone = temp_phone.replace(" (Catering)", "").replace(" X 1", "")
                    hours_of_operation = temp[-1]
                    raw_address = " ".join(x for x in temp[1:-2])

                else:
                    phone = temp[-3].replace(" (Catering)", "")
                    raw_address = " ".join(x for x in temp[1:-3])
                    hours_of_operation = " ".join(x for x in temp[-2:])
                location_name = temp[0]
                log.info(location_name)
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
                yield SgRecord(
                    locator_domain="https://www.pumpernickels.ca/",
                    page_url="https://www.pumpernickels.ca/location",
                    location_name=location_name.strip(),
                    street_address=street_address.strip(),
                    city=city.strip(),
                    state=state.strip(),
                    zip_postal=zip_postal.strip(),
                    country_code="CAN",
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
