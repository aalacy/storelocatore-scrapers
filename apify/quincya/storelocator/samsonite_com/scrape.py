import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-GetNearestStores?format=ajax&countryCode=&distanceUnit=mi&maxResults=10000&postalCode=&otherpostal=&maxdistance=10000"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()["stores"]

    locator_domain = "samsonite.com"

    for store in stores:
        location_name = store["name"]
        raw_address = (store["address1"] + " " + store["address2"]).strip()
        street_address = (
            store["address1"]
            .replace("   ", " ")
            .replace("Crystal Run Mall,", "")
            .replace("Plaza Carolina Mall,", "")
            .replace("(", ",")
            .replace(")", "")
            .replace(" ,", ",")
        )

        if re.search(r"\d", street_address):
            digit = str(re.search(r"\d", street_address))
            start = int(digit.split("(")[1].split(",")[0])
            street_address = street_address[start:]
            if street_address.isdigit():
                street_address = raw_address
        if len(street_address) < 5:
            street_address = raw_address

        words = [
            "center",
            "plaza",
            "shopping",
            "mall",
            "crossing",
            "square",
            "centre",
            "commons",
        ]
        for word in words:
            if word in street_address.lower() and "," in street_address:
                if street_address.lower().rfind(word) > street_address.lower().find(
                    ","
                ):
                    street_address = street_address.split(",")[0]

        if " - " in street_address:
            street_address = street_address.split(" - ")[0]

        street_address = (
            street_address.split(", Unversity")[0]
            .split(", Village")[0]
            .split(", Village")[0]
            .split(", Cerritos")[0]
            .split(", Market")[0]
            .split(", Shopping")[0]
            .split(", Bouquet")[0]
            .split(", Santa")[0]
            .split(", Wesfield ")[0]
            .split(", Shadow")[0]
            .split(", Regency")[0]
            .split(", North ")[0]
            .split(", Dadeland")[0]
            .split(", Melbourne")[0]
            .split("Wrentham")[0]
            .split(", Harlem")[0]
            .split(", Glengarry")[0]
            .split(", Crossings")[0]
            .split(", Fashion ")[0]
            .split(", The")[0]
            .split("Strabane")[0]
            .split(", Katy")[0]
            .split(", Fairlane")[0]
            .split(", Eastgate")[0]
            .replace("Shore Premium Outlets", "Shore")
        ).strip()

        city = store["city"]
        state = store["stateCode"]
        zip_code = store["postalCode"]
        country_code = store["countryCode"]
        store_number = store["storeid"]
        location_type = store["storeType"]
        phone = store["phone"]

        if "closed" in location_name.lower():
            hours_of_operation = "Closed"
        else:
            hours_of_operation = ""
            raw_hours = store["storeHours"]
            hours = list(BeautifulSoup(raw_hours, "lxml").stripped_strings)
            for hour in hours:
                if "hours" not in hour.lower():
                    hours_of_operation = (
                        hours_of_operation + " " + re.sub(", .+: ", " ", hour)
                    ).strip()
            hours_of_operation = (
                hours_of_operation.replace(">", "").replace(" /li>", "").strip()
            )

        latitude = store["latitude"]
        longitude = store["longitude"]
        link = (
            "https://shop.samsonite.com/on/demandware.store/Sites-samsonite-Site/default/Stores-Details?StoreID="
            + store_number
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
                raw_address=raw_address,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
