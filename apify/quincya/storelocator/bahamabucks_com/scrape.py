import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://bahamabucks.com/locations/"
    js_link = "https://bahamabucks.com/wp-content/cache/autoptimize/js/autoptimize_1d947f98a5b19801d376e6c98ccbceff.js"

    session = SgRequests()
    req = session.get(js_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    js = base.text.split("shops:")[1].split(",comingSoon:")[0]
    stores = json.loads(js)

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    items = base.find_all(class_="location-result")

    locator_domain = "bahamabucks.com"

    for store_number in stores:
        store = stores[store_number]
        location_name = store["information"]["shop_location"]
        street_address = (
            (
                store["address"]["line1"].strip()
                + " "
                + store["address"]["line2"].strip()
            )
            .split("Typhoon Texas")[0]
            .split("Cy-Fair")[0]
            .split("Zaraplex")[0]
            .split("Shoppes")[0]
            .split("Minute")[0]
            .strip()
        )
        city = store["address"]["city"]
        state = store["address"]["state"]
        zip_code = store["address"]["zip"]
        country_code = "US"
        location_type = "<MISSING>"
        phone = store["information"]["phone"]
        if not phone:
            phone = "<MISSING>"
        hours_of_operation = ""
        try:
            raw_hours = store["hours"]["current_hours"]
            for day in raw_hours:
                if "day" in day:
                    hours_of_operation = (
                        hours_of_operation + " " + day.title() + " " + raw_hours[day]
                    ).strip()
        except:
            hours_of_operation = "<MISSING>"
        if hours_of_operation.count("Game Days") == 7:
            hours_of_operation = "<MISSING>"
        latitude = store["address"]["latitude"]
        longitude = store["address"]["longitude"]

        for item in items:
            if item["id"].split("-")[1] == store_number:
                link = "https://bahamabucks.com" + item.a["href"].replace(
                    "bayamón", "bayamon"
                )
        if link == "https://bahamabucks.com/shop/":
            link = base_link
        if (
            location_name == "Typhoon Texas"
            and hours_of_operation
            == "Monday Tuesday Wednesday Thursday Friday Saturday Sunday"
        ):
            continue
        if not location_name:
            location_name = "BAHAMA BUCK'S"

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
