import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://pizzacucinova.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.findAll("div", attrs={"class": "inner-content"})

    for item in items:
        link = item.find("a")["href"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        locator_domain = "pizzacucinova.com"
        location_name = base.find("h2").text.strip()

        raw_data = (
            str(base.find("p", attrs={"class": "address"}))
            .replace("<p>", "")
            .replace("</p>", "")
            .replace("\n", "")
            .split("<br/>")
        )
        street_address = raw_data[0][raw_data[0].rfind(">") + 1 :].strip()
        raw_line = raw_data[1]
        city = raw_line[: raw_line.rfind(",")].strip()
        state = raw_line[raw_line.rfind(",") + 1 : raw_line.rfind(" ")].strip()
        zip_code = raw_line[raw_line.rfind(" ") + 1 :].strip()
        country_code = "US"
        store_number = "<MISSING>"
        phone = re.findall(r"[\d]{3}-[\d]{3}-[\d]{4}", str(base.text))[0]
        location_type = "<MISSING>"
        hours_of_operation = (
            base.find("div", attrs={"class": "normal-hours"})
            .get_text(separator=u" ")
            .replace("\n", " ")
            .replace("Normal business hours", "")
            .replace("\xa0", "")
            .strip()
        )
        hours_of_operation = re.sub(" +", " ", hours_of_operation)
        new_base = BeautifulSoup(req.text, "lxml")

        raw_gps = str(new_base)
        start_point = raw_gps.find("latitude") + 10
        latitude = raw_gps[start_point : raw_gps.find(",", start_point)].strip()
        semi_point = raw_gps.find("longitude", start_point)
        longitude = raw_gps[semi_point + 12 : raw_gps.find("}", semi_point)].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
