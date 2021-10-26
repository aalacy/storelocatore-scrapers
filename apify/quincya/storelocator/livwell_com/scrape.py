import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://livwell.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="post-details no-cut")
    locator_domain = "livwell.com"

    for item in items:
        location_name = item.a.text.strip()
        raw_data = item.find(class_="post-description").find_all("p")
        street_address = raw_data[0].text.strip()
        city_line = raw_data[1].text
        city = city_line[: city_line.find(",")].strip()
        state = city_line[city_line.find(",") + 1 : city_line.find(",") + 4].strip()
        zip_code = city_line[-6:].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = raw_data[-1].text.strip()
        phone = item.find_all("a")[-1].text.strip()
        hours_of_operation = raw_data[3].text.replace("Hours:", "").strip()

        link = "https://livwell.com" + item.a["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        latitude = re.findall(r'latitude":"[0-9]{2}\.[0-9]+', str(base))[0].split(":")[
            1
        ][1:]
        longitude = re.findall(r'longitude":"-[0-9]{2,3}\.[0-9]+', str(base))[0].split(
            ":"
        )[1][1:]

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
