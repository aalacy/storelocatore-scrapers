import ssl

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

from sgselenium.sgselenium import SgChrome

session = SgRequests()

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data(sgw: SgWriter):

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
    headers = {"User-Agent": user_agent}

    base_link = "https://www.directtoolsoutlet.com/store-finder"

    driver = SgChrome(user_agent=user_agent).driver()

    driver.get(base_link)
    cookies = driver.get_cookies()
    cookie = ""
    for cook in cookies:
        cookie = cookie + cook["name"] + "=" + cook["value"] + "; "
    cookie = cookie.strip()[:-1]
    driver.close()

    headers = {
        "authority": "www.directtoolsoutlet.com",
        "method": "GET",
        "path": "/api-proxy/rest/api/v2/stores?radius=482802&fields=FULL&pageSize=100&query=",
        "scheme": "https",
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "cookie": cookie,
        "sec-ch-ua": '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"',
        "sec-ch-ua-mobile": "?0",
        "sec-fetch-dest": "document",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.71 Safari/537.36",
    }

    locator_domain = "https://www.directtoolsoutlet.com/"
    base_link = "https://www.directtoolsoutlet.com/api-proxy/rest/api/v2/stores?radius=482802&fields=FULL&pageSize=100&query="

    locs = session.get(base_link, headers=headers).json()["stores"]

    for loc in locs:
        location_name = loc["displayName"]
        if "CLOSED" in location_name.upper():
            continue
        phone_number = loc["address"]["phone"]
        street_address = loc["address"]["line1"]
        try:
            if loc["address"]["line2"] is not None:
                street_address += " " + loc["address"]["line2"]
        except:
            pass

        city = loc["address"]["town"].split(",")[0]
        if "KY" in loc["address"]["town"]:
            state = "KY"
        else:
            state = loc["address"]["region"]["name"]

        zip_code = loc["address"]["postalCode"]
        lat = loc["geoPoint"]["latitude"]
        longit = loc["geoPoint"]["longitude"]

        hours_of_operation = ""
        store_hours = loc["openingHours"]["weekDayOpeningList"]
        for row in store_hours:
            day = row["weekDay"]
            if row["closed"]:
                hours = "Closed"
            else:
                hours = (
                    row["openingTime"]["formattedHour"]
                    + "-"
                    + row["closingTime"]["formattedHour"]
                )
            hours_of_operation = (hours_of_operation + " " + day + " " + hours).strip()

        country_code = "US"
        location_type = "<MISSING>"
        page_url = "https://www.directtoolsoutlet.com/store-finder"
        store_number = loc["address"]["id"]

        sgw.write_row(
            SgRecord(
                locator_domain=locator_domain,
                page_url=page_url,
                location_name=location_name,
                street_address=street_address,
                city=city,
                state=state,
                zip_postal=zip_code,
                country_code=country_code,
                store_number=store_number,
                phone=phone_number,
                location_type=location_type,
                latitude=lat,
                longitude=longit,
                hours_of_operation=hours_of_operation,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.StoreNumberId)) as writer:
    fetch_data(writer)
