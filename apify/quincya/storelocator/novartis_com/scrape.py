from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sglogging import sglog

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

log = sglog.SgLogSetup().get_logger("novartis.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.novartis.com/our-company/contact-us/office-locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="edit-name-list").find_all("option")
    search_list = []

    for i in items:
        item = i["value"]
        if item != "All":
            search_list.append(item)

    locator_domain = "novartis.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    for search in search_list:
        fin_link = (
            "https://www.novartis.com/our-company/contact-us/office-locations?tid=All&name_list="
            + search
        )
        log.info(fin_link)
        response = session.get(fin_link, headers=headers)
        base = BeautifulSoup(response.text, "lxml")

        groupings = base.find_all(class_="view-grouping")

        for group in groupings:
            location_type = group.h3.text.strip()
            items = group.find_all(class_="views-row")
            for item in items:
                location_name = item.find(class_="title").text.strip()
                raw_address = " ".join(
                    list(item.find(class_="address-street").stripped_strings)
                )
                addr = parse_address_intl(raw_address)
                street_address = addr.street_address_1
                if addr.street_address_2:
                    street_address = street_address + " " + addr.street_address_2
                city = addr.city
                state = addr.state
                zip_code = addr.postcode
                country_code = item.find(class_="country").text.strip()

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
                        raw_address2 = list(
                            item.find(class_="address-street").stripped_strings
                        )
                        street_address = " ".join(raw_address2[:-1])

                store_number = "<MISSING>"
                phone = item.find(class_="phone").text.replace("Phone:", "").strip()
                latitude = "<MISSING>"
                longitude = "<MISSING>"
                hours_of_operation = "<MISSING>"
                try:
                    link = item.find(class_="url").a["href"]
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
                    )
                )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
