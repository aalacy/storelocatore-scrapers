from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    locator_domain = "https://toscanova.com"
    req = session.get(locator_domain, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    links = base.find_all(class_="custom-temp-btn")
    link_list = []
    for link in links:
        link_list.append(link["href"])

    for link in link_list:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")
        street_address = base.find(class_="address").text
        city_state = base.find(class_="city-state").text.split(", ")
        city = city_state[0]
        state = city_state[1]
        zip_code = base.find(class_="zip").text
        if zip_code == "":
            zip_code = "<MISSING>"

        hours = (
            " ".join(list(base.find(class_="hours").stripped_strings)[1:])
            .split("Bar")[0]
            .replace("Restaurant Hours:", "")
            .strip()
        )

        phone_number = base.find(id="contact_us_v3_section_phone_link").text

        lat = str(base).split("LATITUDE =")[1].split(";")[0].strip()
        longit = str(base).split("LONGITUDE =")[1].split(";")[0].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"

        start = link.find("//")
        end = link.find(".to")
        location_name = link[start + 2 : end]

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
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
