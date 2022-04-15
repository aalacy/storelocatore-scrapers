import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://fiizdrinks.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://www.fiizdrinks.com"

    response = session.get(base_link, headers=headers)
    base = BeautifulSoup(response.text, "lxml")

    found = []

    sections = base.find(class_="elementor-section-wrap").find_all(
        "section", recursive=False
    )[1:]

    for section in sections:
        items = section.find(
            class_="elementor-container elementor-column-gap-default"
        ).find_all(class_="elementor-widget-wrap elementor-element-populated")
        for item in items:
            if "opening" in item.text.lower() or "coming" in item.text.lower():
                continue
            try:
                location_name = item.h3.text.replace("CREEKCOL", "CREEK COL").strip()
            except:
                continue
            raw_address = list(item.h5.stripped_strings)
            if "188," in raw_address[0]:
                raw_address = raw_address[0].replace("188,", "188RR").split("RR")
            if "land Dr," in raw_address[0]:
                raw_address = (
                    raw_address[0].replace("land Dr,", "land DrRR").split("RR")
                )
            street_address = " ".join(raw_address[:-1])
            if street_address in found:
                continue
            city_line = raw_address[-1]
            city = city_line.split(",")[0]
            state = city_line.split(",")[1].split()[0].strip()
            zip_code = city_line.split(",")[1].split()[1].strip()
            if "Cedar City" in city:
                street_address = city.split("Cedar")[0].strip()
                city = "Cedar City"
            if "Lagoon" not in street_address:
                found.append(street_address)
            country_code = "US"
            location_type = ""
            try:
                hours_of_operation = (
                    " ".join(list(item.table.stripped_strings))
                    .replace(" Weather & Event Permitting", "")
                    .strip()
                )
            except:
                hours_of_operation = ""

            phone = item.a.text.replace("NOW OPEN!", "").strip()
            if not phone[2].isdigit() or "-0000" in phone:
                phone = ""

            if "follow" in hours_of_operation:
                hours_of_operation = ""
            store_number = ""
            try:
                map_str = item.find(string="Directions").find_previous()["href"]
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", map_str)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
            except:
                latitude = ""
                longitude = ""
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


with SgWriter(
    SgRecordDeduper(
        SgRecordID({SgRecord.Headers.LOCATION_NAME, SgRecord.Headers.STREET_ADDRESS})
    )
) as writer:
    fetch_data(writer)
