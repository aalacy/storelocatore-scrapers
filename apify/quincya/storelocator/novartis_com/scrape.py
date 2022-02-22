from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sglogging import sglog

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger("novartis.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.novartis.com/about/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="edit-field-location-country-target-id").find_all("option")
    search_list = []

    for i in items:
        item = i["value"]
        if item:
            search_list.append(item)

    locator_domain = "novartis.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    for search in search_list:
        fin_link = (
            "https://www.novartis.com/about/locations?field_location_business_unit_target_id=All&field_location_country_target_id="
            + search
        )
        log.info(fin_link)
        response = session.get(fin_link, headers=headers)
        base = BeautifulSoup(response.text, "lxml")

        groupings = base.find_all(class_="accordion-group")

        for group in groupings:
            location_type = group.find(class_="accordion-heading").text.strip()
            main_items = group.find_all(class_="item-list")
            for main_item in main_items:
                items = main_item.find_all("li")
                for item in items:
                    location_name = item.find(class_="off-title").text.strip()
                    raw_address = " ".join(
                        list(item.find(class_="off-add").p.stripped_strings)
                    )
                    addr = parse_address_intl(raw_address)
                    street_address = addr.street_address_1
                    if addr.street_address_2:
                        street_address = street_address + " " + addr.street_address_2
                    city = addr.city
                    state = addr.state
                    zip_code = addr.postcode
                    country_code = item.find(class_="off-country").text.strip()

                    if city and city[-1:] == "/":
                        city = city[:-1].strip()

                    if state and state[:1] == "/":
                        state = state[1:].strip()

                    if street_address:
                        if (
                            country_code == "United States"
                            or street_address.replace("-", "").isdigit()
                            or len(street_address) < 13
                        ):
                            street_address = raw_address
                    else:
                        street_address = raw_address

                    if country_code == "United States":
                        if not city or not state:
                            try:
                                city = item.h3.text.split(",")[0].strip()
                                state = item.h3.text.split(",")[1].strip()
                            except:
                                pass
                        if "-" in street_address:
                            street_address = street_address.split("-")[0].strip()

                    str_up = street_address.upper()
                    if state:
                        st_up = " " + state.upper() + " "
                        if st_up in str_up:
                            c_loc = str_up.find(st_up)
                            street_address = street_address[:c_loc].strip()

                    if city:
                        if city in street_address:
                            street_address = street_address[
                                : street_address.rfind(city)
                            ].strip()
                    if state == "Michael" and country_code == "Barbados":
                        city = "St. Michael"
                        state = ""

                    if street_address[-1:] == ",":
                        street_address = street_address[:-1].strip()

                    if len(street_address) < 10:
                        street_address = raw_address

                    str_up = street_address.upper()
                    c_up = country_code.upper()
                    if c_up in str_up:
                        c_loc = str_up.find(c_up)
                        street_address = street_address[:c_loc].strip()

                    if zip_code:
                        if zip_code in street_address:
                            street_address = street_address.replace(zip_code, "")
                        if "-" in zip_code and not zip_code[0].isdigit():
                            zip_code = " ".join(zip_code.split("-")[1:])

                    if "Jardim Pirajussara" in street_address:
                        city = "Jardim Pirajussara"
                        street_address = street_address.replace(
                            "Jardim Pirajussara", ""
                        ).strip()

                    street_address = (
                        street_address.replace("23 AL-", "")
                        .replace("Alger", "")
                        .split("- Cambridge")[0]
                        .strip()
                    )

                    store_number = "<MISSING>"
                    phone = (
                        item.find(class_="off-phone").text.replace("Phone:", "").strip()
                    )
                    if "N" in phone.upper():
                        phone = ""
                    latitude = "<MISSING>"
                    longitude = "<MISSING>"
                    hours_of_operation = "<MISSING>"
                    try:
                        link = item.find(class_="off-url").a["href"]
                        if not link:
                            link = fin_link
                    except:
                        link = fin_link

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


with SgWriter(
    SgRecordDeduper(
        SgRecordID(
            {
                SgRecord.Headers.LOCATION_NAME,
                SgRecord.Headers.LOCATION_TYPE,
                SgRecord.Headers.RAW_ADDRESS,
            }
        )
    )
) as writer:
    fetch_data(writer)
