import re

from bs4 import BeautifulSoup

from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.kedplasma.us/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="city_mobile")
    locator_domain = "kedplasma.us"

    for item in items:
        if "OPENING" in item.text.upper():
            continue
        location_name = item.b.text.strip()
        street_address = item.a.text.split(",")[1].strip()[2:].replace("Canada", "")
        city = item.b.text.split(",")[0].strip().split("-")[0]
        state = item.b.text.split(",")[1].replace("Canada", "").strip()
        zip_code = item.a.text.split(",")[-2].split()[-1]
        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        phone = item.a.text.split(",")[-1]

        if zip_code == "6B6":
            zip_code = "R3T 6B6"
            country_code = "CA"

        link = item.a["href"]
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        hours_of_operation = (
            " ".join(
                (
                    list(base.find(class_="plasma-center-contact-us").stripped_strings)[
                        :-1
                    ]
                )
            )
            .replace("\xa0", " ")
            .replace("Opening hours:", "")
            .split("KEDPLASMA")[0]
            .split("Se hab")[0]
            .strip()
        )
        hours_of_operation = (
            hours_of_operation.encode("ascii", "replace").decode().replace("?", "-")
        )
        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

        if "COMING" in hours_of_operation.upper():
            continue

        all_scripts = base.find_all("script")
        for script in all_scripts:
            if "myLatlng" in str(script):
                script = str(script).replace(", -8", ",-8")
                geo = re.findall(r"[0-9]{2}\.[0-9]+,-[0-9]{2,3}\.[0-9]+", script)[
                    0
                ].split(",")
                latitude = geo[0]
                longitude = geo[1]
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
