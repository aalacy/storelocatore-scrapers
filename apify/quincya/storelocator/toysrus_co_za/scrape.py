from bs4 import BeautifulSoup

from sgpostal.sgpostal import parse_address_intl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.toysrus.co.za"

    all_links = []

    base_link = "https://www.toysrus.co.za/find-a-store"

    for i in range(5):
        response = session.get(base_link, headers=headers)
        base = BeautifulSoup(response.text, "lxml")

        items = base.find_all(class_="action more")
        for item in items:
            link = item["href"]
            all_links.append(link)
        try:
            base_link = base.find(class_="item pages-item-next active").a["href"]
        except:
            break

    for link in all_links:
        response = session.get(link, headers=headers)
        item = BeautifulSoup(response.text, "lxml")
        location_name = item.h1.text.strip()

        raw_address = item.find(class_="address-line").text.replace("\n", " ").strip()
        addr = parse_address_intl(raw_address)
        try:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        except:
            street_address = addr.street_address_1
        city = addr.city
        state = addr.state
        zip_code = addr.postcode

        try:
            if street_address.isdigit():
                street_address = raw_address
        except:
            pass

        country_code = "South Africa"
        location_type = ""
        store_number = ""
        phone = item.find(class_="phone-number").text.strip()
        hours_of_operation = (
            " ".join(list(item.find(class_="working-times").stripped_strings))
            .split("Public")[0]
            .strip()
        )
        map_str = item.find(class_="directions")["href"]
        try:
            geo = map_str.split("=")[-1].split(",")
            latitude = geo[0]
            longitude = geo[1].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
