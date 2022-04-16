from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("thebodyshop_co_uk")


def fetch_data():
    locs = []
    url = "https://www.thebodyshop.com/sitemap-uk.xml"
    r = session.get(url, headers=headers)
    website = "thebodyshop.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.thebodyshop.com/commerce/rest/v2/medias/Store" in line:
            smurl = (
                "https://www.thebodyshop.com/commerce/rest/v2/medias/Store"
                + line.split(
                    "<loc>https://www.thebodyshop.com/commerce/rest/v2/medias/Store"
                )[1].split("<")[0]
            )
            r2 = session.get(smurl, headers=headers)
            for line2 in r2.iter_lines():
                if "<loc>https://www.thebodyshop.com/en-gb/store-details/" in line2:
                    locs.append(line2.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = loc.rsplit("/", 1)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        lurl = (
            "https://api.thebodyshop.com/rest/v2/thebodyshop-uk/stores/"
            + store
            + "?fields=FULL&lang=en_GB&curr=GBP"
        )
        r2 = session.get(lurl, headers=headers)
        info = json.loads(r2.content)
        try:
            add = info["address"]["line1"]
            phone = info["address"]["phone"]
            zc = info["address"]["postalCode"]
            state = "<MISSING>"
            city = info["address"]["town"]
            lat = info["geoPoint"]["latitude"]
            lng = info["geoPoint"]["longitude"]
            name = info["displayName"]
            for item in info["openingHours"]["weekDayOpeningList"]:
                if item["closed"] is True:
                    hrs = item["weekDay"] + ": Closed"
                else:
                    hrs = (
                        item["weekDay"]
                        + ": "
                        + item["openingTime"]["formattedHour"]
                        + "-"
                        + item["closingTime"]["formattedHour"]
                    )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if (
                "DUBLIN" not in city
                and "CORK" not in city
                and "GALWAY" not in city
                and "COUNTY DUB" not in city
            ):
                add = add.replace("Quay,", "Quay")
                add = add.replace("Glasgow Road,", "Glasgow Road")
                add = add.replace("Quays,", "Quays")
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
