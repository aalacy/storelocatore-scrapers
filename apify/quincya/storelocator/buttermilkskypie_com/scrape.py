import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


from sgrequests import SgRequests

logger = SgLogSetup().get_logger("buttermilkskypie_com")


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.buttermilkskypie.com/locations/"

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "buttermilkskypie.com"

    items = base.find_all("a", string="Store Details")

    for item in items:

        if "http" not in item["href"]:
            link = "https://www.buttermilkskypie.com/locations" + item["href"]
        else:
            link = item["href"]
        logger.info(link)

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if (
            "coming soon"
            in base.find(
                class_="et_pb_section et_pb_section_1 et_section_regular"
            ).text.lower()
        ):
            continue

        if (
            "coming in "
            in base.find(
                class_="et_pb_section et_pb_section_1 et_section_regular"
            ).text.lower()
        ):
            continue

        if (
            "coming early"
            in base.find(
                class_="et_pb_section et_pb_section_1 et_section_regular"
            ).text.lower()
        ):
            continue

        location_name = base.h1.text.upper().strip()

        raw_address = list(base.p.stripped_strings)
        if "SERVING" in raw_address[0].upper():
            raw_address.pop(0)

        street_address = raw_address[0].strip()

        if "," not in raw_address[1]:
            street_address = street_address + " " + raw_address[1].strip()
            city_line = raw_address[2].split(",")
        else:
            city_line = raw_address[1].split(",")
        city = city_line[0].strip()
        state = city_line[1][:-6].strip()
        zip_code = city_line[1][-6:].strip()

        if not zip_code.isdigit():
            state = zip_code
            zip_code = "<MISSING>"

        if "6120 Camp Bowie" in street_address:
            zip_code = "76116"

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = base.find_all("p")[1].text.replace("Phone:", "").strip()
        if "," in phone:
            phone = base.find_all("p")[2].text.replace("Phone:", "").strip()

        hours_of_operation = ""
        raw_hours = list(
            base.find(
                class_="et_pb_section et_pb_section_1 et_section_regular"
            ).stripped_strings
        )

        for hour in raw_hours:
            if "day" in hour:
                hours_of_operation = (
                    hours_of_operation + " " + hour.replace("\xa0", "").strip()
                ).strip()
        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        try:
            latitude = base.find(class_="et_pb_map")["data-center-lat"]
            longitude = base.find(class_="et_pb_map")["data-center-lng"]
        except:
            map_str = base.p.a["href"]
            geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[0].split(
                ","
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
