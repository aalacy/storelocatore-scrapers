import json

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    base_link = "https://elranchoinc.com/wp-admin/admin-ajax.php"
    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()

    payload = {
        "lat": "31.9685988",
        "lng": "-99.9018131",
        "store_locatore_search_radius": "500",
        "action": "make_search_request",
    }

    base_link = "https://elranchoinc.com/wp-admin/admin-ajax.php"
    response = session.post(base_link, headers=headers, data=payload)
    base = BeautifulSoup(response.text, "lxml")

    fin_script = ""
    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "lng" in str(script):
            fin_script = (
                str(script)
                .replace("\\", "")
                .replace('"/>', "")
                .replace('"http', "")
                .replace('">', "")
                .replace('class="', "class=")
                .replace('" class', " class")
                .replace("\n", "")
                .strip()
            )
            break

    js = fin_script.split('locations":')[-1].split("};  ")[0].strip()
    stores = json.loads(js)
    items = base.find_all(class_="store-locator-item")

    locator_domain = "elranchoinc.com"

    for i in range(len(stores)):
        store = stores[i]
        item = items[i]
        location_name = item.find(class_="wpsl-name").text.strip()
        street_address = item.find(class_="wpsl-address").text.strip()
        city_line = item.find(class_="wpsl-city").text.strip().split(",")
        city = city_line[0]
        state = city_line[1].split()[0].strip()
        try:
            zip_code = city_line[1].split()[1].strip()
        except:
            zip_code = "<MISSING>"
        if not city:
            city = street_address.split()[-1]
            if "Worth" in city or "Prairie" in city or "Branch" in city:
                city = " ".join(street_address.split()[-2:])
            if "Houston" in street_address:
                city = "Houston"
            street_address = street_address[: street_address.rfind(city)].strip()

        country_code = "US"
        store_number = item["id"]
        location_type = "<MISSING>"
        try:
            phone = item.find(class_="wpsl-phone").text.strip()
        except:
            phone = "<MISSING>"
        hours_of_operation = "<INACCESSIBLE>"
        latitude = store["lat"]
        longitude = store["lng"]
        link = "https://elranchoinc.com/stores-2/"

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
