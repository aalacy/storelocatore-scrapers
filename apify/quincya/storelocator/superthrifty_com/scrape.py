from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.superthrifty.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.superthrifty.com"

    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    items = base.find(string="Locations").find_next("ul").find_all("li")
    for i in items:
        link = i.a["href"]
        response = session.get(link, headers=headers)
        item = BeautifulSoup(response.text, "lxml")

        location_name = item.h1.text.strip()
        raw_address = list(
            item.find(string="Address").find_previous("div").stripped_strings
        )[1:]
        street_address = raw_address[0]
        city = raw_address[1].split(",")[0]
        state = raw_address[1].split(",")[1].strip()
        zip_code = raw_address[2]
        country_code = "CA"
        location_type = ""
        phone = item.find(string="Phone:").find_next().text.strip()

        try:
            hours_of_operation = (
                " ".join(
                    list(
                        item.find(string="Store Hours:")
                        .find_next("table")
                        .stripped_strings
                    )
                )
                .split("Holidays")[0]
                .strip()
            )
        except:
            hours_of_operation = ""
        store_number = (
            item.find(class_="content").find(class_="container").div["id"].split("-")[1]
        )
        latitude = item.find(id="gmap-1")["data-x"]
        longitude = item.find(id="gmap-1")["data-y"]

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
