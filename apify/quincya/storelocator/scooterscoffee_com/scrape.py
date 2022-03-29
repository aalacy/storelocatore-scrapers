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

    session = SgRequests()
    locator_domain = "scooterscoffee.com"

    num = 0
    for i in range(1, 100):
        base_link = (
            "https://code.metalocator.com/index.php?user_lat=0&user_lng=0&postal_code=&radius=100&ml_location_override=&Itemid=12991&view=directory&layout=combined_bootstrap&tmpl=component&framed=1&ml_skip_interstitial=0&preview=0&parent_table=&parent_id=0&task=search_zip&search_type=point&_opt_out=&option=com_locator&limitstart=%s&filter_order=id&filter_order_Dir=asc"
            % num
        )
        req = session.get(base_link, headers=headers)
        base = str(BeautifulSoup(req.text, "lxml"))

        js = base.split("location_data =")[1].split("var search")[0].strip()[:-1]
        stores = json.loads(js)

        if len(stores) == 0:
            break

        for store in stores:
            store_number = store["id"]
            location_name = store["name"]
            if (
                "COMING SOON" in str(store).upper()
                or "permanently closed" in str(store).lower()
            ):
                continue
            try:
                street_address = (store["address"] + " " + store["address2"]).strip()
            except:
                street_address = store["address"]

            if not street_address:
                street_address = "<MISSING>"

            if len(street_address) < 2:
                street_address = "<MISSING>"

            city = store["city"]
            state = store["state"].replace("wav", "VA")
            zip_code = store["postalcode"]
            country_code = "US"
            location_type = "<MISSING>"
            try:
                phone = store["phone"].replace("Pending", "").strip()
                if not phone:
                    phone = "<MISSING>"
            except:
                phone = ""

            try:
                hours_of_operation = (
                    store["hours"]
                    .replace("{", "")
                    .replace("}", " ")
                    .replace("|", " ")
                    .strip()
                )
            except:
                hours_of_operation = ""
            latitude = store["lat"]
            longitude = store["lng"]
            link = "https://www.scooterscoffee.com/locations"

            if "temporarily closed" in location_name.lower():
                hours_of_operation = "Temporarily Closed"

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

        num = num + 15


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
