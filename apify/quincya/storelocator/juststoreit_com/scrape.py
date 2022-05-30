from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://juststoreit.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="multi_city_item data_source")
    locator_domain = "https://juststoreit.com"

    for item in items:
        link = locator_domain + item["link"]

        location_name = item.find(class_="fac_name").text.strip()

        raw_data = list(item.find(class_="city_address").stripped_strings)
        street_address = raw_data[0].strip()
        city_line = raw_data[1].split(",")
        city = city_line[0].strip()
        state = city_line[1].split()[0].strip()
        zip_code = " ".join(city_line[1].split()[1:]).strip()
        country_code = "US"
        location_type = ""
        store_number = ""
        phone = item.find(class_="city_phone").text.strip()
        latitude = item["lat"]
        longitude = item["lng"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = base.find(string="Gate Hours").find_next().text

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
