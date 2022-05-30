from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicZipSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("examone_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

search = DynamicZipSearch(
    country_codes=[SearchableCountries.USA],
    max_search_distance_miles=100,
    max_search_results=None,
)


def fetch_data():
    for code in search:
        logger.info(("Pulling Zip %s..." % code))
        url = (
            "https://www.examone.com/locations/?zipInput="
            + code
            + "&dist=100&submit=find+locations"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if "var php_vars" in line:
                items = line.split('\\"qsl_id\\":\\"')
                for item in items:
                    if "qsl_address" in item:
                        store = item.split("\\")[0]
                        name = "ExamOne"
                        website = "examone.com"
                        typ = "<MISSING>"
                        add = item.split('qsl_address\\":\\"')[1].split("\\")[0]
                        add = (
                            add
                            + " "
                            + item.split('"qsl_address2\\":\\"')[1].split("\\")[0]
                        )
                        city = item.split('"qsl_city\\":\\"')[1].split("\\")[0]
                        state = item.split('"qsl_state\\":\\"')[1].split("\\")[0]
                        zc = item.split('"qsl_zip\\":\\"')[1].split("\\")[0]
                        country = "US"
                        phone = item.split('"qsl_phone\\":\\"')[1].split("\\")[0]
                        add = add.strip()
                        lat = item.split('"qsl_latitude\\":\\"')[1].split("\\")[0]
                        lng = item.split('"qsl_longitude\\":\\"')[1].split("\\")[0]
                        hours = "<MISSING>"
                        loc = "https://www.examone.com/locations/"
                        if "(" in add:
                            if add.count("(") == 1:
                                typ = add.split("(")[1].split(")")[0]
                                add = add.split("(")[0].strip()
                            else:
                                typ = add.split("(")[2].split(")")[0]
                                add = add.split("(")[0].strip()
                        if phone == "":
                            phone = "<MISSING>"
                        if " 405 942" in add:
                            add = add.split(" 405 942")[0]
                        if " 832-" in add:
                            add = add.split(" 832-")[0]
                        if " 800-" in add:
                            add = add.split(" 800-")[0]
                        if " 866-" in add:
                            add = add.split(" 866-")[0]
                        if " 610-" in add:
                            add = add.split(" 610-")[0]
                        if " 877" in add:
                            add = add.split(" 877")[0]
                        if " Ofc#" in add:
                            add = add.split(" Ofc#")[0]
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
            RecommendedRecordIds.GeoSpatialId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
