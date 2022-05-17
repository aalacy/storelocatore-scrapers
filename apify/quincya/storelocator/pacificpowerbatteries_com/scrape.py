from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.pacificpowerbatteries.com"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find("details-disclosure").find_all("li")
    for item in items:
        link = base_link + item.a["href"]
        if "locations" in link:
            continue
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        content = base.find(class_="image-with-text__content")
        if not content:
            content = base.find(class_="rich-text__blocks")
        location_name = content.h2.text.strip()
        city = location_name
        raw_line = list(content.p.stripped_strings)[0]
        location_type = "<MISSING>"
        if "Independently Owned" in raw_line:
            location_type = "Independently Owned"
            raw_line = list(content.p.stripped_strings)[1]
        street_address = raw_line[: raw_line.find(city)].strip()
        state = raw_line[raw_line.rfind(",") + 1 : raw_line.rfind(" ")].strip()
        if "Mountlake Terrace" in state:
            state = "WA"
        zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = content.find_all("p")[-1].a.text
        if "@" in phone:
            phone = content.find_all("p")[-2].a.text
        latitude = "<MISSING>"
        longitude = "<MISSING>"

        hours_of_operation = ""
        rows = list(content.div.stripped_strings)
        for row in rows:
            if ":00" in row or ":" in row[-1]:
                hours_of_operation = (
                    hours_of_operation + " " + row.replace("\xa0", " ")
                ).strip()

        sgw.write_row(
            SgRecord(
                locator_domain=base_link,
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
