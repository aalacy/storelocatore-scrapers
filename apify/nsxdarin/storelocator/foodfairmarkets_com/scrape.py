from sgrequests import SgRequests
from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    base_link = "https://www.foodfairmarkets.com/"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"

    driver = SgChrome(user_agent=user_agent).driver()
    driver.get(base_link)
    token = driver.get_cookie("fp-session")["value"].split("%22")[-2]
    driver.close()

    url = (
        "https://api.freshop.com/1/stores?app_key=foodfair_market&has_address=true&limit=-1&token="
        + token
    )
    items = session.get(url, headers=headers).json()["items"]
    website = "foodfairmarkets.com"
    typ = "<MISSING>"
    country = "US"
    for item in items:
        store = item["id"]
        name = item["name"]
        lat = item["latitude"]
        lng = item["longitude"]
        loc = item["url"]
        add = item["address_1"]
        city = item["city"]
        try:
            state = item["state"]
        except:
            state = "<MISSING>"
        zc = item["postal_code"]
        hours = item["hours_md"]
        try:
            phone = item["phone_md"]
        except:
            phone = "<MISSING>"
        if city == "Ironton":
            state = "OH"
        if city == "West Hamlin":
            state = "WV"
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
