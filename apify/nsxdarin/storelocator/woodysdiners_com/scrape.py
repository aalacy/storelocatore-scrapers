from sgselenium import SgChrome
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

user_agent = (
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:78.0) Gecko/20100101 Firefox/78.0"
)


def fetch_data():
    website = "woodysdiners.com"
    typ = "Restaurant"
    country = "US"
    loc = "<MISSING>"
    store = "<MISSING>"
    url = "https://www.woodysdiners.com/locations"
    loc = "https://www.woodysdiners.com/locations"
    add = "21450 Yorba Linda Blvd."
    city = "Yorba Linda"
    state = "CA"
    zc = "92887"
    phone = "714-779-7013"
    hours = "Sun-Sat: 7am-9pm"
    lat = "33.8773284"
    lng = "-117.7550664"
    name = "Woody's Yorba Linda"
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

    with SgChrome(user_agent=user_agent) as driver:
        driver.get(url)
        driver.implicitly_wait(30)
        website = "woodysdiners.com"
        typ = "Restaurant"
        country = "US"
        store = "<MISSING>"
        text = driver.page_source
        text = str(text).replace("\r", "").replace("\n", "").replace("\t", "")
        items = text.split(',"RestaurantLocation:')
        for item in items:
            if '<html lang="en">' not in item:
                name = item.split('"name":"')[1].split('"')[0]
                loc = "https://www.woodysdiners.com/locations"
                lat = item.split('"lat":')[1].split(",")[0]
                lng = item.split('"lng":')[1].split(",")[0]
                city = item.split('"city":"')[1].split('"')[0]
                state = item.split('"state":"')[1].split('"')[0]
                zc = item.split('"postalCode":"')[1].split('"')[0]
                add = item.split('"streetAddress":"')[1].split('"')[0]
                phone = item.split('"displayPhone":"')[1].split('"')[0]
                try:
                    hours = (
                        item.split('"schemaHours":[')[1]
                        .split("]")[0]
                        .replace('","', "; ")
                    )
                except:
                    hours = "<MISSING>"
                hours = hours.replace('"', "")
                if "21450 Yorba Linda Blvd" not in add:
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
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
