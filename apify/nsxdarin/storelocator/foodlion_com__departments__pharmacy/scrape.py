from sgrequests import SgRequests
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("foodlion_com__departments__pharmacy")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=50,
    max_search_results=None,
)


def fetch_data():
    ids = []
    for code in search:
        logger.info(("Pulling Zip Code %s..." % code))
        url = (
            "https://www.foodlion.com/bin/foodlion/search/storelocator.json?zip="
            + code
            + "&distance=5000&onlyPharmacyEnabledStores=true"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"result":"' in line:
                items = line.split('\\"id\\":')
                for item in items:
                    if '{"result":"' not in item:
                        website = "foodlion.com/departments/pharmacy"
                        typ = "<MISSING>"
                        country = "US"
                        loc = (
                            "https://foodlion.com/stores/"
                            + item.split("lion/stores/")[1].split('\\"')[0]
                        )
                        store = item.split(",")[0]
                        name = item.split('"title\\":\\"')[1].split('\\"')[0]
                        lat = item.split('"lat\\":')[1].split(",")[0]
                        lng = item.split(',\\"lon\\":')[1].split(",")[0]
                        hours = (
                            item.split('\\"hours\\":[\\"')[1]
                            .split('\\"]')[0]
                            .replace('\\",\\"', "; ")
                        )
                        add = item.split('\\"address\\":\\"')[1].split("\\")[0].strip()
                        city = item.split('\\"city\\":\\"')[1].split("\\")[0]
                        state = item.split('\\"state\\":\\"')[1].split("\\")[0]
                        zc = item.split('"zip\\":\\"')[1].split("\\")[0]
                        phone = item.split('"phoneNumber\\":\\"')[1].split("\\")[0]
                        if store not in ids:
                            ids.append(store)
                            r2 = session.get(loc, headers=headers)
                            logger.info(loc)
                            for line2 in r2.iter_lines():
                                if '<span itemprop="telephone">' in line2:
                                    phone = line2.split('<span itemprop="telephone">')[
                                        1
                                    ].split("<")[0]
                                if 'meta itemprop="openingHours" content="' in line2:
                                    hours = line2.split(
                                        'meta itemprop="openingHours" content="'
                                    )[1].split('"')[0]
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
