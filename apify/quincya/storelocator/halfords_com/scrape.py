import json

from bs4 import BeautifulSoup

from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):
    base_link = "https://www.halfords.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    stores = json.loads(base.find(class_="js-stores").contents[0])["stores"]

    locator_domain = "halfords.com"

    for store in stores:
        try:
            location_name = store["name"].replace(" null", "")
        except:
            continue
        try:
            street_address = (store["address1"] + " " + store["address2"]).strip()
        except:
            try:
                street_address = store["address1"].strip()
            except:
                continue
        street_address = street_address.replace("Way Whitstable", "Way").replace(
            "rock, Ess", "rock, Essex"
        )
        city = store["city"]
        try:
            state = store["stateCode"]
        except:
            state = ""
        words = ["Middlesex", "Essex"]
        if not state:
            for word in words:
                if word in street_address:
                    state = word
                    street_address = street_address.replace(word, "").strip()[:-1]

        zip_code = store["postalCode"]
        country_code = "UK"
        try:
            phone = store["phone"]
        except:
            phone = "<MISSING>"
        latitude = store["latitude"]
        longitude = store["longitude"]

        if len(str(latitude)) < 3:
            latitude = "<MISSING>"
            longitude = "<MISSING>"

        store_number = store["ID"]
        link = store["storeDetailsLink"]
        location_type = store["storeType"]
        if not location_type:
            if "auto" in link:
                location_type = "Halfords Autocentre"
            else:
                location_type = "Halfords"

        try:
            hours_of_operation = ""
            raw_hours = store["storeHours"]["workingHours"][0]
            for hour in raw_hours:
                try:
                    time_str = (
                        raw_hours[hour][0]["Start"] + "-" + raw_hours[hour][0]["Finish"]
                    )
                except:
                    time_str = "Closed"
                hours_of_operation = (
                    hours_of_operation + " " + hour + ": " + time_str
                ).strip()
        except:
            hours_of_operation = "<MISSING>"
        try:
            msg = str(store["custom"]["emergencyMessage"])
            if "now closed" in msg:
                continue
            if "currently closed" in msg:
                hours_of_operation = "Currently Closed"
            if "temporarily closed" in msg:
                hours_of_operation = "Temporarily Closed"
        except:
            pass

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
