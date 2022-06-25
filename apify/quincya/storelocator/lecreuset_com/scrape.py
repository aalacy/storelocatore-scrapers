import re
import ssl

from bs4 import BeautifulSoup

from sglogging import sglog

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger("lecreuset_com")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    base_link = "https://www.lecreuset.co.uk/en_GB/stores/cop004.html"

    locator_domain = "lecreuset.com"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    with SgChrome(user_agent=user_agent) as driver:
        log.info(base_link)
        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")

        countries = []
        rows = (
            base.find(id="store-accordion")
            .find(class_="row")
            .find_all("div", {"id": re.compile(r"[A-Z]{2}")})
        )

        for row in rows:
            countries.append([row, base_link])

        continents = base.find_all(class_="mb-3 mb-md-0")[1:]
        for continent in continents:
            link = continent.a["href"]
            log.info(link)
            driver.get(link)
            base = BeautifulSoup(driver.page_source, "lxml")

            rows = (
                base.find(id="store-accordion")
                .find(class_="row")
                .find_all("div", {"id": re.compile(r"[A-Z]{2}")})
            )
            for row in rows:
                countries.append([row, link])

        for i in countries:
            try:
                country = i[0][0]
                link = i[0][1]
            except:
                country = i[0]
                link = i[1]
            if not country:
                continue

            country_code = country.find(class_="h4").text
            items = country.find_all(class_="mb-3")

            for item in items:

                raw_data = list(item.stripped_strings)
                if len(raw_data) == 1:
                    continue

                location_name = raw_data[0].replace("\n", " ").strip()
                log.info(location_name)

                raw_address = " ".join(raw_data[1:-2]).replace("\n", " ")
                if "le creuset shop" in raw_address.lower():
                    location_name = location_name + " " + raw_data[1].replace("\n", " ")
                    raw_address = " ".join(raw_data[2:4]).replace("\n", " ")

                if not raw_address:
                    raw_address = raw_data[1].replace("\n", " ").strip()

                if "UNITED STATES" not in country_code.upper():
                    addr = parse_address_intl(raw_address)
                    try:
                        street_address = (
                            addr.street_address_1 + " " + addr.street_address_2
                        )
                    except:
                        street_address = addr.street_address_1
                    city = (
                        item.find_previous(
                            class_="h4 mb-3 border-bottom-dotted border-lightgray"
                        )
                        .text.replace("The Style Outlets", "")
                        .split(",")[0]
                        .strip()
                    )
                    state = addr.state
                    if state:
                        if state[:2].isdigit():
                            state = ""
                    zip_code = addr.postcode
                    phone = raw_data[-2].strip()
                else:
                    street_address = raw_data[1].strip()
                    city_line = item.find_previous().text.split(",")
                    city = city_line[0].strip()
                    state = city_line[1].strip()
                    zip_code = ""
                    country_code = "United States"
                    phone = raw_data[2].strip()

                if not street_address:
                    continue

                if country_code.upper() == "JAPAN":
                    if not city:
                        city = raw_address.split(",")[2].strip()
                    if len(street_address) < 10:
                        street_address = (
                            " ".join(raw_address.split(",")[:2])
                            .replace(city, "")
                            .replace("Ryuo-cho", "")
                            .strip()
                        )
                if country_code == "UK":
                    try:
                        if " " not in zip_code:
                            zip_code = raw_data[-3]
                    except:
                        zip_code = raw_data[-3]

                if street_address.isdigit():
                    street_address = raw_address.split(",")[0]

                street_address = (
                    street_address.replace("Korea", "")
                    .replace("W1G", "")
                    .replace("N10", "")
                    .strip()
                )

                if "Amsterdam" in city:
                    city = "Amsterdam"

                if city:
                    city = city.replace("\n", " ").replace(" (UP)", " ")

                if "CANADA" in country_code.upper():
                    phone = raw_data[2].strip()
                if len(phone) > 20:
                    phone = raw_data[2].strip()
                if "Halfweg" in phone:
                    phone = raw_data[-1].strip()
                if len(phone) < 3:
                    phone = ""

                store_number = "<MISSING>"
                location_type = "<MISSING>"
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url=link,
                        location_name=location_name,
                        street_address=street_address,
                        city=city,
                        state=state,
                        zip_postal=zip_code,
                        country_code=country_code,
                        store_number=store_number,
                        phone=phone,
                        location_type=location_type,
                        latitude=latitude,
                        longitude=longitude,
                        hours_of_operation=hours_of_operation,
                        raw_address=raw_address,
                    )
                )


with SgWriter(SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))) as writer:
    fetch_data(writer)
