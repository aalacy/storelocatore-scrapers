import json
import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.urthcaffe.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    store_data = base.find_all("script", attrs={"type": "application/ld+json"})

    for i in store_data:
        store = json.loads(i.contents[0])

        street_address = store["address"]["streetAddress"].replace("\n", " ")
        city = store["address"]["addressLocality"]
        state = store["address"]["addressRegion"]
        zip_code = store["address"]["postalCode"]
        location_name = city
        if "459 S. Hewitt" in street_address:
            location_name = "Downtown LA"
        if "3131 S. Las" in street_address:
            location_name = "Wynn Las Vegas"
        if "1 World Way" in street_address:
            location_name = "LAX"
        if "4940 W" in street_address:
            location_name = "South Bay"
        if "8565 Melrose" in street_address:
            location_name = "Melrose"
        country_code = "US"
        location_type = "<MISSING>"
        phone = store["telephone"]
        store_number = ""
        latitude = ""
        longitude = ""
        hours_of_operation = " ".join(store["openingHours"])
        link = (
            "https://www.urthcaffe.com/"
            + location_name.replace(" LA", "").replace(" ", "-").lower()
        )
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        js = str(base.find(id="popmenu-apollo-state"))

        js_ids = re.findall(r"RestaurantLocation:[0-9]+", str(js))
        zips = re.findall(r'postalCode":"[0-9]+', str(js))
        js_lats = re.findall(r'lat":[0-9]{2}\.[0-9]+', str(js))
        js_lngs = re.findall(r'lng":-[0-9]{2,3}\.[0-9]+', str(js))
        for i, z in enumerate(zips):
            if zip_code in z:
                store_number = js_ids[i].split(":")[1]
                latitude = js_lats[i].split(":")[1]
                longitude = js_lngs[i].split(":")[1]
                break

        sgw.write_row(
            SgRecord(
                locator_domain=base_link,
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)) as writer:
    fetch_data(writer)
