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

    base_link = "https://www.mfaoil.com/store-locator-data/?brands=&searchfilters=&lat=38.9331391&lng=-92.3738037&maxdist=100000"

    session = SgRequests()
    stores = session.get(base_link, headers=headers).json()

    locator_domain = "https://www.mfaoil.com"

    for store in stores:
        location_name = store["location_name"].replace("<br>", " ").replace("<br/>", "")
        if "Big O" in location_name:
            continue
        street_address = store["address"]
        city = store["city"]
        state = store["state"]
        zip_code = store["zipCode"]
        country_code = "US"
        store_number = store["id"]
        location_type = ""
        raw_types = store["amenities"]
        for row in raw_types:
            try:
                if row.isdigit():
                    row = raw_types[row]
            except:
                pass
            if row["alt"]:
                location_type = (location_type + ", " + row["alt"]).strip()
        if location_type[:1] == ",":
            location_type = location_type[1:]
        phone = store["phone"]
        latitude = store["latitude"]
        longitude = store["longitude"].replace("-91769", "-91.769")
        link = locator_domain + store["url"]

        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        store_number = base.body["class"][-1].split("-")[-1]
        hours_of_operation = ""
        try:
            hours_of_operation = base.find(class_="fueling").text.strip()
        except:
            pass
        try:
            raw_hours = (
                " ".join(list(base.find(class_="hours").stripped_strings))
                .split("Location")[0]
                .strip()
            )
            hours_of_operation = (hours_of_operation + " " + raw_hours).strip()
        except:
            pass
        if not location_type:
            try:
                location_type = ", ".join(
                    list(base.find(class_="aminities").stripped_strings)
                ).strip()
            except:
                pass

        hours_of_operation = (re.sub(" +", " ", hours_of_operation)).strip()

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
