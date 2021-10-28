import re

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()


def fetch_data(sgw: SgWriter):

    base_link = "https://www.ulta.com/stores"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "https://www.ulta.com"

    all_scripts = base.find_all("script")
    for script in all_scripts:
        if "metaCustomSlug" in str(script):
            data = script.contents[0]
            break

    raw_ids = re.findall(r'id":[0-9]+', data)

    # Split ids into chunks of 100
    L = range(len(raw_ids))
    id_range = [L[x : x + 100] for x in range(0, len(L), 100)]

    for i in id_range:
        ids = []
        for x in i:
            ids.append(raw_ids[x].replace('id":', ""))
        fin_ids = "%2C".join(ids)
        base_link = (
            "https://sls-api-service.sweetiq-sls-production-east.sweetiq.com/aXyQneW52YL8dmJYjXdkvR4t8Sv6Qe/locations-details?locale=en_US&ids="
            + fin_ids
            + "&clientId=5e3da261df2763dd5ce605ab&cname=ulta-sweetiq-sls-production.sweetiq.com"
        )

        stores = session.get(base_link, headers=headers).json()["features"]
        for store in stores:
            store_data = store["properties"]
            if store_data["isPermanentlyClosed"]:
                continue
            location_name = store_data["mallName"]
            try:
                street_address = (
                    store_data["addressLine1"] + " " + store_data["addressLine2"]
                ).strip()
            except:
                street_address = store_data["addressLine1"].strip()
            city = store_data["city"]
            state = store_data["province"]
            store_zip = store_data["postalCode"].strip()
            if len(store_zip) == 4:
                store_zip = "0" + store_zip
            country_code = store_data["country"]
            phone = store_data["phoneNumber"]
            store_number = store_data["branch"]
            page_url = store_data["website"]
            latitude = store["geometry"]["coordinates"][1]
            longitude = store["geometry"]["coordinates"][0]
            location_type = ", ".join(store_data["services"])
            if "Sun" in store_data["hoursOfOperation"]:
                for Sun in store_data["hoursOfOperation"]["Sun"]:
                    sun_time = "Sun: " + Sun[0] + " - " + Sun[1]
            else:
                sun_time = ""
            for Sat in store_data["hoursOfOperation"]["Sat"]:
                sat_time = "Sat: " + Sat[0] + " - " + Sat[1]
            for Fri in store_data["hoursOfOperation"]["Fri"]:
                fri_time = "Fri: " + Fri[0] + " - " + Fri[1]
            for Thu in store_data["hoursOfOperation"]["Thu"]:
                thu_time = "Thu: " + Thu[0] + " - " + Thu[1]
            for Wed in store_data["hoursOfOperation"]["Wed"]:
                wed_time = "Wed: " + Wed[0] + " - " + Wed[1]
            for Tue in store_data["hoursOfOperation"]["Tue"]:
                tue_time = "Tue: " + Tue[0] + " - " + Tue[1]
            for Mon in store_data["hoursOfOperation"]["Mon"]:
                mon_time = "Mon: " + Sat[0] + " - " + Mon[1]
            hour = (
                mon_time
                + ", "
                + tue_time
                + ", "
                + wed_time
                + ", "
                + thu_time
                + ", "
                + fri_time
                + ", "
                + sat_time
                + ", "
                + sun_time
            )
            if hour == "" or hour is None:
                hour = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=page_url,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=store_zip,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hour,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
