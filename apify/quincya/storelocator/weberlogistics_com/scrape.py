import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.weberlogistics.com/locations/west-coast-warehousing"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    links = base.find(class_="span6").find_all("a")

    items = base.find_all(class_="interactive-map-tabs-item")
    locator_domain = "weberlogistics.com"

    for i, item in enumerate(items):

        raw_address = list(item.stripped_strings)[1:]
        street_address = raw_address[0].strip()
        city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "Distribution Center"
        try:
            phone = raw_address[2]
        except:
            phone = "<MISSING>"
        hours_of_operation = "<MISSING>"

        if "http" not in item.a["href"]:
            link = "https://www.weberlogistics.com" + item.a["href"]
        else:
            link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        location_name = base.h1.text.strip()

        try:
            if "855-GO-WEBER" in base.find(id="hslayout_body").text:
                phone = "855-GO-WEBER"
        except:
            pass

        try:
            map_link = base.iframe["src"]
            req = session.get(map_link, headers=headers)
            map_str = BeautifulSoup(req.text, "lxml")
            geo = (
                re.findall(r"\[[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+\]", str(map_str))[0]
                .replace("[", "")
                .replace("]", "")
                .split(",")
            )
            latitude = geo[0]
            longitude = geo[1]
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        for i in links:
            if "data-link" in str(i) and link in str(i):
                if "style-03-blue" in str(i):
                    location_type = "Transportation Service Center"
                elif "style-02" in str(i):
                    location_type = (
                        "Distribution Center & Transportation Service Center"
                    )
                break

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
