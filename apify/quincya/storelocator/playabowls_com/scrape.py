from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.playabowls.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="locations-box")
    locator_domain = "playabowls.com"

    for i, item in enumerate(items):
        location_name = item.h4.text.strip()

        raw_address = list(item.find(class_="locations-address").stripped_strings)
        street_address = raw_address[0].strip()
        if street_address[-1:] == ",":
            street_address = street_address[:-1]
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        try:
            zip_code = city_line[-1].strip().split()[1].strip()
        except:
            zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = item.find(class_="store-number").text.strip()
        except:
            phone = "<MISSING>"
        try:
            hours_of_operation = item.find(class_="locations-timing").text.strip()
        except:
            hours_of_operation = "<MISSING>"
        map_link = item.find(class_="store-directions")["href"]
        latitude = map_link.split("=")[-1].split("%20")[0].replace(",", "")
        longitude = map_link.split("=")[-1].split("%20")[1]
        link = item.find(class_="store-profile")["href"]

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
