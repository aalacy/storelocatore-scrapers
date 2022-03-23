import json
import re
import ssl

from bs4 import BeautifulSoup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgselenium.sgselenium import SgChrome

URL = "https://www.games-workshop.com/"

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    driver = SgChrome(user_agent=user_agent).driver()

    base_links = [
        "https://www.games-workshop.com/en-US/store/fragments/resultsJSON.jsp?latitude=40.2475923&radius=20000&longitude=-77.03341790000002",
        "https://www.games-workshop.com/en-GB/store/fragments/resultsJSON.jsp?latitude=53.2362&radius=500&longitude=-1.42718",
    ]

    for base_link in base_links:

        driver.get(base_link)
        base = BeautifulSoup(driver.page_source, "lxml")
        stores = json.loads(base.text)["locations"]
        for store in stores:
            if store["type"] == "independentRetailer":
                continue

            # Store ID
            location_id = (
                store["storeId"]
                if "storeId" in store.keys()
                else store["id"].split("-")[-1]
            )

            # Country
            country = store["country"] if "country" in store.keys() else "<MISSING>"

            # Name
            location_title = (
                store["name"].strip() if "name" in store.keys() else "<MISSING>"
            )

            # Street
            try:
                street_address = store["address1"] + " " + store["address2"]
            except:
                street_address = store["address1"]

            street_address = (re.sub(" +", " ", street_address)).strip()

            if re.search(r"\d", street_address):
                digit = str(re.search(r"\d", street_address))
                start = int(digit.split("(")[1].split(",")[0])
                street_address = street_address[start:]

            # State
            state = store["state"] if "state" in store.keys() else "<MISSING>"

            if country == "GB":
                state = store["county"] if "county" in store.keys() else "<MISSING>"

            # city
            city = store["city"] if "city" in store.keys() else "<MISSING>"

            # zip
            zipcode = (
                store["postalCode"].replace(" -", "-").replace("L24R 3N1", "L2R 3N1")
                if "postalCode" in store.keys()
                else "<MISSING>"
            )
            if len(zipcode) == 4:
                zipcode = "0" + zipcode

            # store type
            store_type = "<MISSING>"

            # Lat
            lat = store["latitude"] if "latitude" in store.keys() else "<MISSING>"

            # Long
            lon = store["longitude"] if "longitude" in store.keys() else "<MISSING>"
            if lon == -76593137.0:
                lon = -76.593137

            # Phone
            phone = (
                store["telephone"].strip()
                if "telephone" in store.keys()
                else "<MISSING>"
            )
            if phone[:2] == "00":
                phone = phone[2:]
            if len(phone) < 8:
                phone = "<MISSING>"
            # hour
            hour = "<MISSING>"

            link = (
                "https://www.games-workshop.com/en-" + country + "/" + store["seoUrl"]
            )

            sgw.write_row(
                SgRecord(
                    locator_domain=URL,
                    page_url=link,
                    location_name=location_title,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zipcode,
                    country_code=country,
                    store_number=location_id,
                    phone=phone,
                    location_type=store_type,
                    latitude=lat,
                    longitude=lon,
                    hours_of_operation=hour,
                )
            )
    driver.close()


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
