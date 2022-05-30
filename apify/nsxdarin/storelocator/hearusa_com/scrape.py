from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("hearusa_com")

session = SgRequests(verify_ssl=False)
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=100,
    expected_search_radius_miles=100,
    max_search_results=100,
)


def fetch_data():
    locs = []
    for clat, clng in search:
        logger.info(str(clat) + "," + str(clng))
        url = (
            "https://www.hearusa.com/wp-admin/admin-ajax.php?action=store_search&lat="
            + str(clat)
            + "&lng="
            + str(clng)
            + "&max_results=100&search_radius=100&filter=28"
        )
        try:
            r = session.get(url, headers=headers)
            for item in json.loads(r.content):
                lurl = item["permalink"].replace("\\", "")
                if lurl not in locs:
                    locs.append(lurl)
        except:
            pass
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "hearusa.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        city = ""
        state = ""
        add = ""
        zc = ""
        country = "US"
        lat = ""
        phone = ""
        lng = ""
        store = "<MISSING>"
        Found = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<h2 class="centers__header__title">' in line2:
                name = (
                    line2.split('<h2 class="centers__header__title">')[1]
                    .split("<")[0]
                    .replace("&#8211;", "-")
                )
            if '"lat":"' in line2:
                lat = line2.split('"lat":"')[1].split('"')[0]
                lng = line2.split('"lng":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                zc = line2.split('"zip":"')[1].split('"')[0]
                city = line2.split('"city":"')[1].split('"')[0]
                add = line2.split('"address":"')[1].split('"')[0]
                store = line2.split(',"id":')[1].split("}")[0]
                try:
                    add = add + " " + line2.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                except:
                    add = add.strip()
                add = (
                    add.split("N The")[0]
                    .replace("SUITE", "Suite")
                    .replace("STE", "Suite")
                    .replace("Ste", "Suite")
                    .replace("Sumner Plaza", "")
                    .replace("313 #313", "313")
                    .replace("B2 Unit B-2", "B2")
                    .strip()
                )
                words = ["Suite", "Building", "#", "Unit", "C-", "B-"]
                for word in words:
                    if add.count(word) > 1:
                        add = add[: add.rfind(word)].strip()
            if "Customers:" in line2:
                if "New Customers:" in line2:
                    phone = line2.split("New Customers:")[1].split("<")[0].strip()
                elif "Existing Customers:" in line2:
                    phone = line2.split("Existing Customers:")[1].split("<")[0].strip()
                else:
                    phone = line2.split("Customers:")[1].split("<")[0].strip()
            if '<div class="centers__header__hours">' in line2:
                Found = True
            if Found and "</div>" in line2:
                Found = False
            if Found and "Hours:</p>" not in line2 and "<p>" in line2:
                hrs = line2.split("<p>")[1].split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        hours = hours.split("; Sun")[0].strip()

        if lat != "" and lng != "":
            search.found_location_at(lat, lng)

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
