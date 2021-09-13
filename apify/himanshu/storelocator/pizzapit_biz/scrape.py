from bs4 import BeautifulSoup
import re

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_url = "https://pizzapit.biz/locations/"
    r = session.get(base_url)
    soup = BeautifulSoup(r.text, "lxml")
    data = soup.find(class_="page-content").find_all("p")

    locator_domain = "pizzapit.biz"

    for i in data:
        try:
            location_name = i.strong.text.strip()
        except:
            continue
        raw_address = list(i.stripped_strings)[-2:]
        street_address = raw_address[0]
        city_line = raw_address[-1].strip().split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = list(i.stripped_strings)[-3]
        hours_of_operation = "<MISSING>"

        link = i.a["href"]
        r = session.get(link)
        base = BeautifulSoup(r.text, "lxml")

        map_link = base.find(class_="fl-map").iframe["src"]
        req = session.get(map_link)
        map_str = BeautifulSoup(req.text, "lxml")
        geo = (
            re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
            .replace("[", "")
            .replace("]", "")
            .split(",")
        )
        latitude = geo[0]
        longitude = geo[1]

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
