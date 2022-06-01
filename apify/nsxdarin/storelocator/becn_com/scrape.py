from sgrequests import SgRequests
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

logger = SgLogSetup().get_logger("becn_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    for llat, llng in search:
        x = llat
        y = llng
        logger.info(("Pulling Lat-Long %s,%s..." % (str(x), str(y))))
        url = (
            "https://site.becn.com/api-man/StoreLocation?facets=&lat="
            + str(x)
            + "&long="
            + str(y)
            + "&range=100"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '"name":"' in line:
                items = line.split('"name":"')
                for item in items:
                    if '"addressLine1":' in item:
                        name = item.split('"')[0]
                        store = "<MISSING>"
                        website = "becn.com"
                        add = item.split('"addressLine1":"')[1].split('"')[0]
                        add2 = item.split('"addressLine2":"')[1].split('"')[0]
                        add = add + " " + add2
                        add = add.strip()
                        city = item.split('"city":"')[1].split('"')[0]
                        zc = item.split('"postalcode":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        country = item.split('"country":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        hours = "<MISSING>"
                        loc = "https://www.becn.com/find-a-store"
                        phone = item.split('"phone":"')[1].split('"')[0]
                        if country == "UNITED STATES":
                            country = "US"
                        typ = item.split('"branchname":"')[1].split('"')[0]
                        name = name + " " + typ
                        if phone == "":
                            phone = "<MISSING>"
                        if country == "US":
                            if "*" in add:
                                add = add.split("*")[0].strip()
                            name = typ
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
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.COUNTRY_CODE,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
