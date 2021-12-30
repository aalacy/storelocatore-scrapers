import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://chebahut.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_links = []

    items = base.find_all("h2", {"class": re.compile(r"title-heading.+")})
    raw_links = base.find_all(class_="fusion-column-inner-bg hover-type-none")
    for raw_link in raw_links:
        all_links.append(raw_link.a["href"])

    locator_domain = "chebahut.com"

    for i, link in enumerate(all_links):
        raw_address = items[i].text.split(",")
        street_address = raw_address[0].strip()
        city = raw_address[1].strip()
        state = raw_address[-1].strip()
        zip_code = "<MISSING>"
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "Open"

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        if "coming soon" in base.find(class_="title-heading-center").text.lower():
            continue

        location_name = "CHEBA HUT - " + base.h1.text.strip()
        if location_name == "CHEBA HUT - ":
            location_name = "CHEBA HUT - " + city

        if "Opening" in location_name:
            location_type = "Open" + location_name.split("Open")[1]
            location_name = location_name.split("Open")[0].strip()

        raw_data = list(base.find(class_="content-container").stripped_strings)

        phone = raw_data[1].replace("TBA", "<MISSING>")
        hours_of_operation = (
            " ".join(raw_data[4:]).replace("Opening March 1st", "").strip()
        )

        if (
            not hours_of_operation
            or "Monday: Tuesday: Wednesday: Thursday: Friday: Saturday: Sunday:"
            in hours_of_operation
        ):
            continue

        try:
            map_link = base.find(class_="content-container").find_all("a")[-1]["href"]
            zip_code = re.findall(r"\+[\d]{5}", map_link)[0].replace("+", "")
        except:
            pass
        script = str(base.find(class_="wpgmza_map"))
        latitude = script.split('map_start_lat":"')[1].split('",')[0]
        longitude = script.split('map_start_lng":"')[1].split('",')[0]

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
