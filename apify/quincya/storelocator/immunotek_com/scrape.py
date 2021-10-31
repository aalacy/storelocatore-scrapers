import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.immunotek.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "immunotek.com"

    sections = base.find(
        class_="et_pb_section et_pb_section_2 et_pb_with_background et_section_regular"
    ).find_all("div", recursive=False)
    for section in sections:
        items = section.find_all("div", recursive=False)
        for item in items:
            if not list(item.stripped_strings):
                continue
            if "coming-soon" in str(item):
                continue

            location_name = "ImmunoTek " + item.p.text.split(",")[0].strip()

            raw_address = list(item.find_all("p")[2].stripped_strings)
            street_address = raw_address[0].replace("Rd,", "Rd.")
            city = raw_address[1].split(",")[0]
            state = raw_address[1].split(",")[1].split()[0]
            zip_code = raw_address[1].split(",")[1].split()[1]
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.find_all("p")[1].text

            map_str = item.find_all("p")[2].a["href"]
            try:
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = " ".join(
                list(item.find_all(class_="et_pb_text_inner")[-1].stripped_strings)
            ).strip()

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=base_link,
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
