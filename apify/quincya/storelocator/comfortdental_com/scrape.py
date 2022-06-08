import json
from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    locator_domain = "https://comfortdental.com"

    base_link = "https://comfortdental.com/find-a-dentist/"

    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if '"lng"' in str(script):
            script = str(script).replace("%", "")
            break

    js = script.split('"places":')[1].split(',"map_tabs')[0]
    stores = json.loads(js)

    for store_data in stores:
        link = store_data["location"]["extra_fields"]["post_link"]
        location_name = store_data["title"].replace("#038;", "").replace("&#8217;", "'")
        raw_address = list(
            BeautifulSoup(
                store_data["location"]["extra_fields"]["address"], "lxml"
            ).stripped_strings
        )
        street_address = " ".join(raw_address[:-1])
        city = (
            store_data["location"]["extra_fields"]["address"]
            .split("addr'>")[-1]
            .split(",")[0]
        )
        state = store_data["location"]["extra_fields"]["state"]
        zip_code = store_data["location"]["extra_fields"]["zip_code"]
        phone = store_data["location"]["extra_fields"]["phone"]
        country_code = "US"
        location_type = ""
        store_number = store_data["id"]
        latitude = store_data["location"]["lat"]
        longitude = store_data["location"]["lng"]
        hours = store_data["location"]["extra_fields"]
        hours_of_operation = (
            "Mon "
            + hours["hours_monday"]
            + " Tue "
            + hours["hours_tuesday"]
            + " Wed "
            + hours["hours_wednesday"]
            + " Thu "
            + hours["hours_thursday"]
            + " Fri "
            + hours["hours_friday"]
            + " Sat "
            + hours["hours_saturday"]
        )

        try:
            hours_of_operation = hours_of_operation + " Sun " + hours["hours_sunday"]
        except:
            pass

        if "office location" in hours_of_operation:
            hours_of_operation = ""

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
