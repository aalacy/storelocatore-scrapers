import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://www.caesars.com/harrahs"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    final_links = []

    locator_domain = "caesars.com"

    items = base.find_all(class_="card-slider")
    for item in items:
        js = str(item).replace("&quot;", '"').split('items":')[1].split('}"')[0]
        item_js = json.loads(js)
        for i in item_js:
            final_links.append(i["path"])

    for link in final_links:
        req = session.get(link, headers=headers)
        base = BeautifulSoup(req.text, "lxml")

        try:
            location_name = base.h1.text.replace("Welcome to", "").strip()
            raw_address = list(
                base.find(class_="footer-hotel-address").stripped_strings
            )
            street_address = raw_address[0]
            city = raw_address[1].split(",")[0]
            state = raw_address[1].split(",")[1].split()[0]
            zip_code = raw_address[1].split(",")[1].split()[1]
            phone = raw_address[2].replace("Tel:", "").strip()
        except:
            js = str(
                base.find(
                    class_="location aem-GridColumn aem-GridColumn--default--12"
                ).contents[0]
            ).replace("&quot;", '"')
            store_data = json.loads(js.split('model="')[1].split('" id')[0])
            location_name = store_data["header"]
            street_address = store_data["locationAddressLine1"]
            city = store_data["locationAddressLine2"].split(",")[0]
            state = store_data["locationAddressLine2"].split(",")[1].split()[0]
            zip_code = store_data["locationAddressLine2"].split(",")[1].split()[1]
            phone = store_data["locationPhoneNumber"]

        country_code = "US"
        store_number = "<MISSING>"
        location_type = "<MISSING>"
        latitude = "<MISSING>"
        longitude = "<MISSING>"
        hours_of_operation = "<MISSING>"

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
