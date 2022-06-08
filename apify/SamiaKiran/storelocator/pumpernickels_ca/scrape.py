import re
from sglogging import sglog
from bs4 import BeautifulSoup
from sgrequests import SgRequests
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgpostal.sgpostal import parse_address_intl
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
website = "pumpernickels_ca"
log = sglog.SgLogSetup().get_logger(logger_name=website)
session = SgRequests()


DOMAIN = "https://www.pumpernickels.ca/"
MISSING = SgRecord.MISSING

headers = {
    "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "Upgrade-Insecure-Requests": "1",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}


def fetch_data():
    if True:
        url = "https://www.pumpernickels.ca/location"
        r = session.get(url, headers=headers)
        soup = BeautifulSoup(r.text, "html.parser")
        loclist = soup.find("div", {"class": "location-custom-div"}).findAll("p")
        for loc in loclist:
            coords = loc.findAll("u")
            if not coords:
                continue
            if len(coords) > 1:
                temp_list = loc.get_text(separator="|", strip=True).split("DIRECTIONS")[
                    :-1
                ]
                if len(coords) != len(temp_list):
                    coords = coords[1:]
                for temp, coord in zip(temp_list, coords):
                    temp_coord = coord.find("a")["href"].split("@")[1].split(",")
                    latitude = temp_coord[0]
                    longitude = temp_coord[1]
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
                    raw_address = raw_address.replace(",", " ").replace(
                        "(Food Court)", ""
                    )
                    pa = parse_address_intl(raw_address)

                    street_address = pa.street_address_1
                    street_address = street_address if street_address else MISSING

                    city = pa.city
                    city = city.strip() if city else MISSING

                    state = pa.state
                    state = state.strip() if state else MISSING

                    zip_postal = pa.postcode
                    zip_postal = zip_postal.strip() if zip_postal else MISSING
                    log.info(location_name)
                    yield SgRecord(
                        locator_domain=DOMAIN,
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
                        raw_address=raw_address,
                    )

            else:
                temp_coord = loc.find("u").find("a")["href"].split("@")[1].split(",")
                latitude = temp_coord[0]
                longitude = temp_coord[1]
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
                raw_address = raw_address.replace(",", " ")
                location_name = temp[0]
                log.info(location_name)
                pa = parse_address_intl(raw_address)

                street_address = pa.street_address_1
                street_address = street_address if street_address else MISSING

                city = pa.city
                city = city.strip() if city else MISSING

                state = pa.state
                state = state.strip() if state else MISSING

                zip_postal = pa.postcode
                zip_postal = zip_postal.strip() if zip_postal else MISSING
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
                    raw_address=raw_address,
                )


def scrape():
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS}
            )
        )
    ) as writer:
        for item in fetch_data():
            writer.write_row(item)


if __name__ == "__main__":
    scrape()
