from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgpostal.sgpostal import parse_address_intl


def fetch_data(sgw: SgWriter):

    locator_domain = "https://www.obica.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.obica.com/restaurants"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="restaurant-link")

    for item in items:
        if "/restaurants/" in item["href"]:
            link = locator_domain + item["href"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = item.h2.text
            try:
                raw_address = base.find(class_="restaurant-info-wrap").p.a.get_text(" ")
            except:
                continue
            phone = (
                base.find(class_="restaurant-contact-link")
                .text.replace("​", "")
                .strip()
            )
            hours_of_operation = (
                " ".join(
                    list(base.find(class_="restaurant-hours-wrap").stripped_strings)[1:]
                )
                .split("Aperitivo")[0]
                .split("Brunch")[0]
                .strip()
            )
            latitude = ""
            longitude = ""
        elif "/pages/" in item["href"]:
            link = item["href"]
            req = session.get(link, headers=headers)
            base = BeautifulSoup(req.text, "lxml")

            location_name = base.find(class_="shopInfo").tr.td.text
            raw_address = base.find(class_="shopInfo").find_all("tr")[1].td.text
            phone = (
                base.find(class_="shopInfo")
                .find_all("tr")[-2]
                .td.text.replace("TEL：", "")
                .replace("​", "")
                .strip()
            )
            hours_of_operation = (
                base.find(class_="shopInfo")
                .find_all("tr")[-1]
                .td.text.replace("\n", " ")
                .strip()
            )
            map_link = base.find(class_="shop-map").iframe["src"]
            lat_pos = map_link.rfind("!3d")
            latitude = map_link[lat_pos + 3 : map_link.find("!", lat_pos + 5)].strip()
            lng_pos = map_link.find("!2d")
            longitude = map_link[lng_pos + 3 : map_link.find("!", lng_pos + 5)].strip()

        city = item.find(class_="restaurant-item-city").text.split(",")[0].strip()
        country_code = (
            item.find(class_="restaurant-item-city").text.split(",")[-1].strip()
        )

        hours_of_operation = hours_of_operation.replace(")Dinner", ") Dinner").replace(
            "  ", " "
        )
        addr = parse_address_intl(raw_address)
        street_address = addr.street_address_1
        if addr.street_address_2:
            street_address = addr.street_address_1 + " " + addr.street_address_2
        state = addr.state
        zip_code = addr.postcode
        store_number = ""
        location_type = ""

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
