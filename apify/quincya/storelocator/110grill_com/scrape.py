import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.110grill.com/locations"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    raw_data = base.find(id="popmenu-apollo-state").contents[0]
    js = raw_data.split("STATE =")[1].strip()[:-1].replace('scr" + "ipt', "script")
    store_data = json.loads(js)

    items = base.find(class_="pm-location-search-list").find_all("section")

    locator_domain = "https://www.110grill.com"

    for i, item in enumerate(items):
        link = locator_domain + item.find("a", class_="pagebutton")["href"]
        if "-" not in link:
            continue
        location_name = item.h4.text
        street_address = item.p.span.text.replace("\xa0", " ").strip()
        city_line = list(item.p.a.stripped_strings)[-1].split(",")
        city = city_line[0].replace(" MA", "").strip()
        state = city_line[-1].strip().split()[0].strip()
        zip_code = city_line[-1].strip().split()[1].strip()
        country_code = "US"
        location_type = "<MISSING>"
        hours_of_operation = " ".join(list(item.find(class_="hours").stripped_strings))
        try:
            phone = item.find_all("a", {"href": re.compile(r"tel:.+")})[0].text.strip()
        except:
            try:
                req = session.get(link, headers=headers)
                base = BeautifulSoup(req.text, "lxml")
                phone = base.find_all("a", {"href": re.compile(r"tel:.+")})[
                    0
                ].text.strip()
            except:
                phone = ""

        store_number = ""
        latitude = ""
        longitude = ""

        for loc in store_data:
            if "RestaurantLocation:" in loc:
                store = store_data[loc]
                if zip_code in store["postalCode"]:
                    store_number = store["id"]
                    latitude = store["lat"]
                    longitude = store["lng"]

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
