import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.junzi.kitchen/visit"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(class_="col sqs-col-12 span-12").find_all(class_="row sqs-row")
    locator_domain = "junzi.kitchen"

    for item in items:

        location_name = item.div.strong.text

        raw_address = json.loads(item.find_all("div")[-2]["data-block-json"])[
            "location"
        ]
        street_address = raw_address["addressLine1"]
        if street_address == "2896 Broadway":
            city = "New York"
            state = "NY"
            zip_code = "10025"
        else:
            city = raw_address["addressLine2"].split(",")[0].strip()
            state = raw_address["addressLine2"].split(",")[1].strip()
            zip_code = raw_address["addressLine2"].split(",")[2].strip()

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        try:
            phone = re.findall(r"[(\d)]{3}-[\d]{3}-[\d]{4}", str(item.text))[0]
        except:
            phone = "<MISSING>"
        next_line = ""
        if "temporarily closed" in item.text:
            hours_of_operation = "temporarily closed"
        else:
            try:
                hours_of_operation = str(item.p).split("<br/>")[-3]
                try:
                    next_line = item.find_all("p")[1].text.strip()
                except:
                    pass
            except:
                hours_of_operation = item.find_all("p")[2].text.strip()
            if "am" not in hours_of_operation and "pm" not in hours_of_operation:
                hours_of_operation = str(item.p).split("<br/>")[-1].replace("</p>", "")
            if " pm" in next_line:
                hours_of_operation = (
                    hours_of_operation + " " + next_line.split("Store")[0].strip()
                )
            hours_of_operation = (
                hours_of_operation.replace(" –", "-")
                .replace("–", "-")
                .replace(" - ", "-")
            )
            if "am" not in hours_of_operation and "pm" not in hours_of_operation:
                hours_of_operation = "<MISSING>"
        latitude = raw_address["mapLat"]
        longitude = raw_address["mapLng"]

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
