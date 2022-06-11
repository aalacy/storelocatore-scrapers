import ssl
import time

from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

from sgselenium.sgselenium import SgChrome

session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}

ssl._create_default_https_context = ssl._create_unverified_context


def fetch_data():

    base_link = "https://www.foodlandstores.com/my-store/store-locator"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    time.sleep(5)

    token = ""
    cookies = driver.get_cookies()
    for cook in cookies:
        if cook["name"] == "fp-session":
            token = cook["value"].split("A%22")[1].split("%22")[0]
            break
    driver.close()

    url = (
        "https://api.freshop.com/1/stores?app_key=foodland_unfi&has_address=true&limit=-1&token="
        + token
    )
    r = session.get(url, headers=headers)
    website = "foodlandstores.com"
    country = "US"
    typ = "<MISSING>"
    for line in r.iter_lines():
        line = str(line)
        if '{"id":"' in line:
            items = line.split('{"id":"')
            for item in items:
                if '"name":"' in item:
                    store = item.split('"')[0]
                    name = item.split('"name":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    loc = item.split('"url":"')[1].split('"')[0]
                    try:
                        add = item.split('"address_0":"')[1].split('"')[0]
                    except:
                        add = ""
                    add = add + " " + item.split('"address_1":"')[1].split('"')[0]
                    add = add.strip()
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"state":"')[1].split('"')[0]
                    zc = item.split('"postal_code":"')[1].split('"')[0]
                    hours = item.split('"hours_md":"')[1].split('"')[0]
                    phone = item.split('"phone_md":"')[1].split('"')[0]
                    hours = hours.replace("Hours: ", "")
                    yield SgRecord(
                        locator_domain=website,
                        page_url=loc,
                        location_name=name,
                        street_address=add,
                        city=city,
                        state=state,
                        zip_postal=zc,
                        country_code=country,
                        phone=phone,
                        location_type=typ,
                        store_number=store,
                        latitude=lat,
                        longitude=lng,
                        hours_of_operation=hours,
                    )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
