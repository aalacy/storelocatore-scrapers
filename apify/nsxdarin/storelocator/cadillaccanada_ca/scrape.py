from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("cadillaccanada_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "host": "www.cadillacoffers.ca",
    "x-requested-with": "XMLHttpRequest",
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.CANADA],
    max_search_distance_miles=None,
    max_search_results=None,
)


def fetch_data():
    for zipcode in search:
        zcode = zipcode[:3] + "%20" + zipcode[-3:]
        url = (
            "https://www.cadillacoffers.ca/apps/leap/readDealersJson?searchType=postalCodeSearch&postalCode="
            + zcode
            + "&language=en&pagePath=%2Fcontent%2Fcadillac-offers%2Fca%2Fen%2Fdealer-locations&_=1653070881080"
        )
        logger.info("Pulling Code %s..." % zcode)
        try:
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"dealerCode":"' in line:
                    items = line.split('"dealerCode":"')
                    for item in items:
                        if '"cpoisId":"' in item:
                            name = item.split('"dealerName":"')[1].split('"')[0]
                            store = item.split('"')[0]
                            lat = item.split('"latitude":')[1].split(",")[0]
                            lng = item.split('"longitude":')[1].split(",")[0]
                            add = item.split('"streetAddress1":"')[1].split('"')[0]
                            if '"streetAddress2":"' in item:
                                add = (
                                    add
                                    + " "
                                    + item.split('"streetAddress2":"')[1].split('"')[0]
                                )
                            city = item.split('"city":"')[1].split('"')[0]
                            zc = item.split('"postalCode":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            country = "CA"
                            try:
                                phone = item.split('"primaryPhone":"')[1].split('"')[0]
                            except:
                                phone = "<MISSING>"
                            if phone == "<MISSING>":
                                try:
                                    phone = item.split('"salesPhone":"')[1].split('"')[
                                        0
                                    ]
                                except:
                                    phone = "<MISSING>"
                            typ = "Dealer"
                            try:
                                purl = item.split('"websiteURL":"')[1].split('"')[0]
                            except:
                                purl = "<MISSING>"
                            website = "cadillaccanada.ca"
                            try:
                                hours = (
                                    "Sun: Closed; Mon: "
                                    + item.split('"salesMondayOpen":"')[1].split('00"')[
                                        0
                                    ]
                                    + "-"
                                    + item.split('"salesMondayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                                hours = (
                                    hours
                                    + "; Tue:"
                                    + item.split('"salesTuesdayOpen":"')[1].split(
                                        '00"'
                                    )[0]
                                    + "-"
                                    + item.split('"salesTuesdayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                                hours = (
                                    hours
                                    + "; Wed:"
                                    + item.split('"salesWednesdayOpen":"')[1].split(
                                        '00"'
                                    )[0]
                                    + "-"
                                    + item.split('"salesWednesdayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                                hours = (
                                    hours
                                    + "; Thu:"
                                    + item.split('"salesThursdayOpen":"')[1].split(
                                        '00"'
                                    )[0]
                                    + "-"
                                    + item.split('"salesThursdayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                                hours = (
                                    hours
                                    + "; Fri:"
                                    + item.split('"salesFridayOpen":"')[1].split('00"')[
                                        0
                                    ]
                                    + "-"
                                    + item.split('"salesFridayClose":"')[1].split(
                                        '00"'
                                    )[0]
                                )
                                try:
                                    hours = (
                                        hours
                                        + "; Sat:"
                                        + item.split('"salesSaturdayOpen":"')[1].split(
                                            '00"'
                                        )[0]
                                        + "-"
                                        + item.split('"salesSaturdayClose":"')[1].split(
                                            '00"'
                                        )[0]
                                    )
                                except:
                                    hours = hours + "; Sat: Closed"
                            except:
                                hours = "Sun-Sat: Closed"
                            logger.info("Pulling Store ID #%s..." % store)
                            yield SgRecord(
                                locator_domain=website,
                                page_url=purl,
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
        deduper=SgRecordDeduper(
            RecommendedRecordIds.PageUrlId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
