import ssl
import time

from bs4 import BeautifulSoup

from sglogging import sglog

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

log = sglog.SgLogSetup().get_logger("guess.eu")

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    session = SgRequests()

    base_link = "https://www.guess.eu/en/StoreLocator"

    user_agent = (
        "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
    )

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    time.sleep(30)
    base = BeautifulSoup(driver.page_source, "lxml")

    cookies = driver.get_cookies()
    cookie = ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "
    cookie = cookie.strip()[:-1]
    driver.close()

    token = base.find(id="dwfrm_storeLocator").find_all("input")[-2]["value"]
    recaptcha = base.find(id="dwfrm_storeLocator").find_all("input")[-1]["value"]

    base_link = "https://www.guess.eu/on/demandware.store/Sites-guess_fr-Site/en/Stores-SearchStores"

    headers = {
        "authority": "www.guess.eu",
        "method": "POST",
        "path": "/on/demandware.store/Sites-guess_fr-Site/en/Stores-SearchStores",
        "scheme": "https",
        "accept": "application/json, text/javascript, */*; q=0.01",
        "accept-encoding": "gzip, deflate",
        "accept-language": "en-US,en;q=0.9",
        "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
        "cookie": cookie,
        "origin": "https://www.guess.eu",
        "referer": "https://www.guess.eu/en/StoreLocator",
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "Linux",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36",
        "x-requested-with": "XMLHttpRequest",
    }

    locator_domain = "https://www.guess.eu"
    found = []

    loc_types = []
    types = base.find(id="storeLocatorType").find_all("option")[1:]
    for i in types:
        loc_types.append(i["id"])
    loc_types.append("")

    countries = base.find(id="country").find_all("option")[1:]
    for i in countries:
        country = i["id"]
        log.info(country)

        for loc_type in loc_types:
            payload = {
                "dwfrm_storeLocator_storeLocatorCountry": country,
                "dwfrm_storeLocator_storeLocatorCity": "*",
                "dwfrm_storeLocator_storeLocatorType": loc_type,
                "csrf_token": token,
                "g-recaptcha-response": recaptcha,
            }

            req = session.post(base_link, headers=headers, data=payload)
            if req.status_code == 200:
                try:
                    stores = req.json()["storeList"]["stores"]
                except:
                    continue
            else:
                log.info(req.status_code)
                continue

            for store in stores:
                location_name = store["name"]
                street_address = store["address1"]
                city = store["city"]
                try:
                    state = store["stateCode"]
                except:
                    state = ""
                zip_code = store["postalCode"]
                country_code = store["countryCode"]
                store_number = store["ID"]
                try:
                    phone = store["phone"]
                except:
                    phone = ""
                location_type = loc_type
                hours_of_operation = ""
                latitude = store["latitude"]
                longitude = store["longitude"]

                if latitude == 0:
                    latitude = ""
                    longitude = ""

                try:
                    raw_address = (store["address1"] + " " + store["address2"]).strip()
                except:
                    raw_address = street_address

                try:
                    if len(street_address) < 5:
                        street_address = raw_address
                except:
                    street_address = raw_address

                if street_address:
                    street_address = (
                        street_address.replace("?", "")
                        .split(", Kiev")[0]
                        .split("- temporary")[0]
                        .split("London Shopping")[0]
                        .replace("Centre Commerc", "")
                        .replace("Livingston Designer Outlet,", "")
                        .replace("Guess Store - ", "")
                        .strip()
                    )
                    if street_address[-1:] == ",":
                        street_address = street_address[:-1]

                try:
                    if street_address + loc_type in found:
                        continue
                    found.append(street_address + loc_type)
                except:
                    pass

                sgw.write_row(
                    SgRecord(
                        locator_domain=locator_domain,
                        page_url="https://www.guess.eu/en/StoreLocator",
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


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
