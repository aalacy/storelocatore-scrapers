from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requeted-with": "XMLHttpRequest",
}

logger = SgLogSetup().get_logger("albertsonsmarket_com")


def fetch_data():
    url = "https://www.albertsonsmarket.com/RS.Relationshop/StoreLocation/GetAllStoresPosition"
    payload = {
        "__RequestVerificationToken": "HSH41-zsqM68f4O03Sh4nZ7uZJsCC9YE9rHD0DU5k0Rasrtst10nLxtbp4MlwIyUdwlb9IlXBNZQO2gWAHkvhjjmwDg1"
    }
    r = session.post(url, headers=headers, data=payload)
    website = "albertsonsmarket.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"Active":' in line:
            items = line.split('{"Active":')
            for item in items:
                if '"Logo":"' in item:
                    name = item.split('"StoreName":"')[1].split('"')[0]
                    city = item.split('"City":"')[1].split('"')[0]
                    add = item.split('"Address1":"')[1].split('"')[0]
                    store = item.split('"StoreID":')[1].split(",")[0]
                    loc = "https://www.albertsonsmarket.com/rs/StoreLocator?id=" + store
                    state = item.split('"State":"')[1].split('"')[0]
                    zc = item.split('"Zipcode":"')[1].split('"')[0]
                    phone = item.split('"PhoneNumber":"')[1].split('"')[0]
                    lat = item.split('"Latitude":')[1].split(",")[0]
                    lng = item.split('"Longitude":')[1].split(",")[0]
                    try:
                        hours = item.split('"StoreHours":"')[1].split('"')[0]
                    except:
                        hours = "<MISSING>"
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
