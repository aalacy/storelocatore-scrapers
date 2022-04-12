import json
import re

from bs4 import BeautifulSoup
from sgrequests import SgRequests

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper


def fetch_data(sgw: SgWriter):

    base_link = "https://www.wegmans.com/stores/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find(id="wegmans-maincontent").find_all(
        "a", href=re.compile("/stores/")
    )
    locator_domain = "wegmans.com"

    for i, item in enumerate(items):
        link = "https://www.wegmans.com" + item["href"]
        if "comhttps" in link:
            link = item["href"]
        location_name = item.text.strip()

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store_js = base.find(class_="yoast-schema-graph").text
        store = json.loads(store_js)
        try:
            raw_data = store["@graph"][1]["description"]
            if "Store Opening" in raw_data:
                continue
        except:
            continue

        raw_address = raw_data.split("•")[0].strip().split(",")
        city = raw_address[-2].strip()
        state = raw_address[-1].strip().split()[0].strip()
        if "New" in state:
            state = "NY"
        if "North" in state:
            state = "NC"
        zip_code = raw_address[-1].strip().split()[-1].replace(".", "").strip()

        if "•" in raw_data:
            street_address = " ".join(raw_address[:-2]).strip()
            phone = raw_data.split("•")[1].strip()
            if len(phone) > 15:
                phone = re.findall(r"[0-9]{3}-[0-9]{3}-[0-9]{4}", raw_data)[0]
        else:
            try:
                street_address = (
                    raw_data[raw_data.rfind("at") + 3 : raw_data.rfind(city)]
                    .replace(",", "")
                    .strip()
                )
                phone = re.findall(r"[0-9]{3}-[0-9]{3}-[0-9]{4}", raw_data)[0]
            except:
                phone = ""
        try:
            if not phone:
                phone = base.find(class_="phone").text.strip()
        except:
            phone = ""

        if "11051 Ligon Mill" in city:
            street_address = "11051 Ligon Mill Rd."
            city = "Wake Forest"

        if not street_address:
            continue

        if "Chapel Hill" in street_address:
            street_address = street_address.replace("Chapel Hill", "").strip()
            city = "Chapel Hill"
            state = "NC"
            zip_code = "27514"

        if "Fairport-Marsh Roads" in street_address:
            street_address = "851 Fairport Road"

        country_code = "US"
        store_number = base.find(id="store-number").text

        types = base.find_all(class_="directions-subhead")
        location_type = ""
        for raw_type in types:
            location_type = (location_type + ", " + raw_type.text).strip()
        location_type = location_type[2:].strip().replace("\n", "")
        location_type = (re.sub(" +", " ", location_type)).strip()

        hours_of_operation = (
            base.find(class_="row map-content").find_all(class_="row")[2].text.strip()
        )
        if "To comply" in hours_of_operation:
            hours_of_operation = hours_of_operation[
                : hours_of_operation.find("To comply")
            ].strip()

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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
