from sgrequests import SgRequests
import json
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("scs_co_uk")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    for x in range(50, 59):
        for y in range(-8, 1):
            logger.info("%s-%s..." % (str(x), str(y)))
            url = (
                "https://www.scs.co.uk/on/demandware.store/Sites-SFRA_SCS-Site/en_GB/Stores-FindStores?showMap=true&radius=1000.0&lat="
                + str(x)
                + "&long="
                + str(y)
                + "&storeCount=5&searchKey="
            )
            r = session.get(url, headers=headers)
            for item in json.loads(r.content)["stores"]:
                name = item["name"]
                website = "scs.co.uk"
                try:
                    add = item["address1"] + " " + item["address2"]
                except:
                    add = item["address1"]
                add = add.strip()
                city = item["city"]
                try:
                    state = item["stateCode"]
                except:
                    state = "<MISSING>"
                zc = item["postalCode"]
                lat = item["latitude"]
                lng = item["longitude"]
                phone = item["phone"]
                country = item["countryCode"]
                store = item["ID"]
                typ = "<MISSING>"
                purl = "https://www.scs.co.uk/stores/" + item["storeTag"]
                hours = ""
                hrinfo = item["openingHoursTable"]
                hrinfo = (
                    hrinfo.replace("\\r", "")
                    .replace("\\n", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
                days = hrinfo.split('<td class="day">')
                try:
                    for day in days:
                        if "b-store-hours" not in day:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split('class="hour">')[1].split("<")[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                except:
                    hours = "<MISSING>"
                phone = phone.replace('"', "'")
                if "tel:" in phone:
                    phone = phone.split("tel:")[1].split("'")[0]
                if "0" not in phone and "1" not in phone:
                    phone = "<MISSING>"
                phone = phone.replace("Pre Delivery:", "").strip()
                if "," in phone:
                    phone = phone.split(",")[0].strip()
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
