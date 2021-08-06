from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dairyqueen_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_radius_miles=25,
    max_search_results=None,
)


def fetch_data():
    locs = []
    for lat, lng in search:
        url = (
            "https://prod-dairyqueen.dotcmscloud.com/api/vtl/locations?country=us&lat="
            + str(lat)
            + "&long="
            + str(lng)
        )
        r = session.get(url, headers=headers)
        logger.info(str(lat) + "-" + str(lng))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '"address3":"' in line:
                items = line.split('"address3":"')
                for item in items:
                    if '"url":"' in item:
                        lurl = (
                            "https://www.dairyqueen.com/en-ca"
                            + item.split('"url":"')[1].split('"')[0]
                        )
                        if lurl not in locs:
                            locs.append(lurl)
    url = "https://www.dairyqueen.com/en-us/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "dairyqueen.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if (
            "<loc>https://www.dairyqueen.com/en-us/locations/" in line
            and "-us/locations/</loc>" not in line
        ):
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        zc = ""
        store = loc.rsplit("/", 2)[1]
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h1 class="my-1 h2">' in line2:
                name = line2.split('<h1 class="my-1 h2">')[1].split("<")[0]
            if '"address3":"' in line2:
                add = line2.split('"address3":"')[1].split('"')[0]
                lat = line2.split('"latlong":"')[1].split(",")[0]
                lng = line2.split('"latlong":"')[1].split(",")[1].replace('"', "")
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"stateProvince":"')[1].split('"')[0]
                try:
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                try:
                    phone = line2.split('"phone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
            if '{"miniSiteHours":' in line2:
                days = line2.split('{"miniSiteHours":')[1].split('","')[0]
                try:
                    hours = "Sun: " + days.split("1:")[1].split(",")[0]
                except:
                    hours = "Sun: Closed"
                try:
                    hours = hours + "; Mon: " + days.split(",2:")[1].split(",")[0]
                except:
                    hours = "Mon: Closed"
                try:
                    hours = hours + "; Tue: " + days.split(",3:")[1].split(",")[0]
                except:
                    hours = "Tue: Closed"
                try:
                    hours = hours + "; Wed: " + days.split(",4:")[1].split(",")[0]
                except:
                    hours = "Wed: Closed"
                try:
                    hours = hours + "; Thu: " + days.split(",5:")[1].split(",")[0]
                except:
                    hours = "Thu: Closed"
                try:
                    hours = hours + "; Fri: " + days.split(",6:")[1].split(",")[0]
                except:
                    hours = "Fri: Closed"
                try:
                    hours = hours + "; Sat: " + days.split(",7:")[1]
                except:
                    hours = "Sat: Closed"
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        name = name.replace("&amp;", "&").replace("&amp", "&")
        add = add.replace("&amp;", "&").replace("&amp", "&")
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
