from bs4 import BeautifulSoup
import re
import json

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.selectphysicaltherapy.com//sxa/search/results/?s={D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}|{D779ED53-C5AD-46DB-AA4F-A2F78783D3B1}&itemid={29966A67-0D55-4E7D-968A-88849BF32EF3}&sig=&autoFireSearch=true&v={99A28EFC-3607-4C5B-8D33-D37C5B70E2EF}&p=3000&g=&o=Distance,Ascending"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    new_base = (
        str(base)
        .replace("</li><li>", ",")
        .replace("<br/>", ",,")
        .replace('<img src="h', " ,,DDD")
        .replace('"/>', "DDD,,")
        .replace("Request an Appointment", ",,")
        .replace("Featured Services", ",,")
    )
    final_base = BeautifulSoup(new_base, "lxml")
    store = json.loads(final_base.text)["Results"]

    for item in store:
        locator_domain = "selectphysicaltherapy.com"

        raw_data = item["Html"].split(",,")
        location_name = raw_data[0].strip()

        raw_type = (
            raw_data[-3]
            .replace("DDDt", "ht")
            .replace("DDD", "")
            .split("/op/")[1]
            .split("---")[0]
            .split(".png")[0]
        )

        if "Select-Physical-Therapy" not in raw_type:
            continue

        location_type = raw_data[-1].strip()

        if len(raw_data) == 7:
            street_address = raw_data[1].strip() + " " + raw_data[2].strip()
            city_line = raw_data[3].strip()
        else:
            street_address = raw_data[1].strip()
            city_line = raw_data[2].strip()

        city = city_line[: city_line.find(",")].strip()
        state = city_line[city_line.find(",") + 1 : city_line.find(",") + 5].strip()
        zip_code = city_line[city_line.find("(") - 7 : city_line.find("(")].strip()
        country_code = "US"

        store_number = "<MISSING>"
        phone = city_line.split("\r")[1].strip()
        if phone == "(817) 333-018":
            phone = "(817) 333-0181"
        hours = (
            raw_data[-2]
            .replace("Hours", "")
            .replace("PM", "PM ")
            .replace("Closed", "Closed ")
            .strip()
        )
        hours_of_operation = re.sub(" +", " ", hours)

        if not hours_of_operation:
            hours_of_operation = "<MISSING>"

        latitude = item["Geospatial"]["Latitude"]
        longitude = item["Geospatial"]["Longitude"]

        link = (
            "https://www.selectphysicaltherapy.com/contact/find-a-location"
            + item["Url"].split("outpatient")[-1]
        )

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
