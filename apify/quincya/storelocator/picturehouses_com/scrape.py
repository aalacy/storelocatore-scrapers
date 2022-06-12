from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.picturehouses.com/cinema?search="

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    HEADERS = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=HEADERS)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="cinemaPage_list cinema_desktop_view").find_all(
        class_="hovereffect"
    )
    locator_domain = "picturehouses.com"

    for item in items:
        link = item.a["href"] + "/information"
        req = session.get(link, headers=HEADERS)
        base = BeautifulSoup(req.text, "lxml")

        try:
            raw_address = list(base.find(class_="cinemaAdrass").stripped_strings)
        except:
            continue

        location_name = raw_address[0].replace("amp;", "")
        street_address = raw_address[1].replace("–", "-").strip()
        city = raw_address[-2].strip()
        if "Street" in city:
            street_address = raw_address[-2].strip()
            city = raw_address[1].strip()
        if "," in city:
            street_address = street_address + " " + city.split(",")[0]
            city = city.split(",")[1].strip()

        state = "<MISSING>"
        zip_code = raw_address[-1].strip()
        country_code = "GB"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = "<MISSING>"
        try:
            hours_of_operation = (
                base.find(id="opening-times")
                .text.replace("Opening Times", "")
                .replace("each day.", "")
                .replace("every day and close around", "-")
                .strip()
            )
        except:
            hours_of_operation = "<MISSING>"
        if "Downstairs" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("Downstairs")
            ].strip()
        if "Due" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("Due")
            ].strip()
        if "Mon-Sat" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                hours_of_operation.find("Mon-Sat") :
            ].strip()
        if "before" in hours_of_operation:
            hours_of_operation = "<MISSING>"
        if "at " in hours_of_operation:
            hours_of_operation = hours_of_operation[
                hours_of_operation.find("at") + 2 :
            ].strip()
        if hours_of_operation[-1:] == ".":
            hours_of_operation = hours_of_operation[:-1]
        if "m" not in hours_of_operation.lower():
            hours_of_operation = "Mon-Sun: " + hours_of_operation
        try:
            raw_gps = base.find(class_="location_map").iframe["src"]
            latitude = raw_gps[raw_gps.find("=") + 1 : raw_gps.find(",")].strip()
            longitude = raw_gps[raw_gps.find(",") + 1 : raw_gps.find("&")].strip()
        except:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

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
