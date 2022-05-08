from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("riteaid_com__pharmacy")

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=None,
    max_search_results=None,
)

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    for zipcode in search:
        logger.info(("Pulling Postal Code %s..." % zipcode))
        url = (
            "https://www.riteaid.com/services/ext/v2/stores/getStores?address="
            + str(zipcode)
            + "&radius=100&pharmacyOnly=true&globalZipCodeRequired=true"
        )
        r = session.get(url, headers=headers)
        country = "US"
        typ = "Rite-Aid Pharmacy"
        lines = r.iter_lines()
        website = "riteaid.com/pharmacy"
        for line in lines:
            if '{"storeNumber":' in line:
                items = line.split('{"storeNumber":')
                for item in items:
                    if '"address":"' in item:
                        store = item.split(",")[0]
                        logger.info(str(store))
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"zipcode":"')[1].split('"')[0]
                        phone = item.split('"fullPhone":"')[1].split('"')[0]
                        lat = item.split('"latitude":')[1].split(",")[0]
                        lng = item.split('"longitude":')[1].split(",")[0]
                        name = "Rite Aid #" + store
                        hours = ""
                        lurl = "https://www.riteaid.com/locations/" + store
                        try:
                            r2 = session.get(lurl, headers=headers)
                            for line2 in r2.iter_lines():
                                if "Pharmacy Hours</h3>" in line2:
                                    days = (
                                        line2.split("Pharmacy Hours</h3>")[1]
                                        .split("data-showOpenToday")[0]
                                        .split('"day":"')
                                    )
                                    for day in days:
                                        if '"intervals"' in day:
                                            try:
                                                hrs = (
                                                    day.split('"')[0]
                                                    + ": "
                                                    + day.split('"start":')[1].split(
                                                        "}"
                                                    )[0]
                                                    + "-"
                                                    + day.split('"end":')[1].split(",")[
                                                        0
                                                    ]
                                                )
                                            except:
                                                hrs = day.split('"')[0] + ": Closed"
                                            if hours == "":
                                                hours = hrs
                                            else:
                                                hours = hours + "; " + hrs
                            if hours == "":
                                hours = "<MISSING>"
                            hours = (
                                hours.replace("1000", "10:00")
                                .replace("1100", "11:00")
                                .replace("1200", "12:00")
                                .replace("1300", "13:00")
                                .replace("1400", "14:00")
                                .replace("1500", "15:00")
                                .replace("1600", "16:00")
                                .replace("1700", "17:00")
                                .replace("1800", "18:00")
                                .replace("1900", "19:00")
                            )
                            hours = hours.replace("1730", "17:30").replace(
                                "2130", "21:30"
                            )
                            hours = (
                                hours.replace("2000", "20:00")
                                .replace("2100", "21:00")
                                .replace("2200", "22:00")
                                .replace("2300", "23:00")
                                .replace("600", "6:00")
                                .replace("700", "7:00")
                                .replace("800", "8:00")
                                .replace("900", "9:00")
                            )
                            yield SgRecord(
                                locator_domain=website,
                                page_url=lurl,
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
                        except:
                            pass


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
