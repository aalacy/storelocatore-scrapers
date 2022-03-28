import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://pinnacletreatment.com/locations/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "pinnacletreatment.com"

    sections = base.find(class_="locations-select").find_all("option")[1:]
    for section in sections:
        state_link = section["value"]
        req = session.get(state_link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        items = base.find(id="locations-grid").find_all("li")

        for item in items:
            if "coming soon" in item.text.lower():
                continue

            location_name = item.h2.text.strip()

            raw_address = list(
                item.find(class_="locations-grid-address").stripped_strings
            )
            if "Same Day" in raw_address[-1]:
                raw_address.pop(-1)
            if "Walk-in" in raw_address[-1]:
                raw_address.pop(-1)
            if "admissions" in raw_address[-1]:
                raw_address.pop(-1)
            street_address = " ".join(raw_address[:-3])
            city = raw_address[-3].split(",")[0].replace("5th St", "").strip()
            state = raw_address[-3].split(",")[1].split()[0]
            zip_code = raw_address[-3].split(",")[1].split()[1]
            country_code = "US"
            store_number = "<MISSING>"
            location_type = "<MISSING>"
            phone = item.find(class_="listing-grid-phone").text.split(",")[0].strip()

            link = item.a["href"]
            req = session.get(link, headers=headers)
            page_base = BeautifulSoup(req.text, "lxml")
            if (
                "coming soon" in page_base.find(class_="entry-content").text.lower()
                or "opening fall" in page_base.find(class_="entry-content").text.lower()
            ):
                continue

            try:
                map_link = page_base.find(id="locations-map").find_all("iframe")[-1][
                    "src"
                ]
                lat_pos = map_link.rfind("!3d")
                latitude = map_link[
                    lat_pos + 3 : map_link.find("!", lat_pos + 5)
                ].strip()
                lng_pos = map_link.find("!2d")
                longitude = map_link[
                    lng_pos + 3 : map_link.find("!", lng_pos + 5)
                ].strip()
            except:
                latitude = "<MISSING>"
                longitude = "<MISSING>"

            hours_of_operation = ""
            try:
                hours_of_operation = " ".join(
                    page_base.find(class_="right")
                    .text.strip()
                    .split("\n\r\n")[0]
                    .split("Hours:")[1:]
                ).strip()
                if len(hours_of_operation) < 10 and "24" not in hours_of_operation:
                    hours_of_operation = (
                        page_base.find(class_="right")
                        .text.strip()
                        .split("\n\r\n")[0]
                        .split("Hours:")[2]
                        .strip()
                    )
                hours_of_operation = (
                    hours_of_operation.replace("\r\n", " ")
                    .replace("\nGroups:", " Groups:")
                    .split("\n\n")[0]
                    .replace("Clinic:", "")
                    .replace("Clinic", "")
                    .replace("We're open", "")
                    .strip()
                )

                if hours_of_operation == "Dispensing:":
                    hours_of_operation = (
                        " ".join(
                            page_base.find(class_="right")
                            .text.strip()
                            .split("\n\r\n")[0]
                            .split("Office Hours:")[1:]
                        )
                        .strip()
                        .split("\n")[0]
                        .strip()
                    )

                if hours_of_operation == "Hours of Operation:":
                    hours_of_operation = (
                        " ".join(
                            page_base.find(class_="right")
                            .text.strip()
                            .split("Operation:\n\r\n")[1:]
                        )
                        .split("\n\r\n")[0]
                        .replace("\r\n", " ")
                    ).strip()
            except:
                hours_of_operation = ""

            if (
                " Hours" in hours_of_operation
                and "Holiday Hours" not in hours_of_operation
            ):
                hours_of_operation.split(" Hours")[1].strip()

            hours_of_operation = (
                hours_of_operation.split("*")[0]
                .replace("Administrative", "")
                .replace("Office", "")
                .replace("Office:", "")
                .replace("Dispensing", "")
                .replace("Medication", "")
                .replace("Methadone:", "")
                .replace("Dosing", "")
                .replace("Business:", "")
                .replace(": Mon", "Mon")
                .replace("Hours", "")
                .replace("  ", " ")
                .replace("\n", " ")
                .split("Groups:")[0]
                .split("Licenses:")[0]
                .split("Out of")[0]
                .split("Walk")[0]
                .split("OBOT")[0]
            ).strip()

            if (
                " Hours" in hours_of_operation
                and "Holiday Hours" not in hours_of_operation
            ):
                hours_of_operation = hours_of_operation.split("Hours ")[1].strip()

            hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

            if (
                not hours_of_operation
                and "opening " in page_base.find(class_="entry-content").text.lower()
            ):
                continue

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
