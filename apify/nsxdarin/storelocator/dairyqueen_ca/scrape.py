from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dairyqueen_com")

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.CANADA],
    max_search_distance_miles=None,
    max_search_results=50,
)


def fetch_data():
    locs = ["https://www.dairyqueen.com/en-ca/locations/on/ajax/250-bayly-st-w/1993/"]
    for lat, lng in search:
        time.sleep(1)
        url = (
            "https://prod-dairyqueen.dotcmscloud.com/api/vtl/locations?country=ca&lat="
            + str(lat)
            + "&long="
            + str(lng)
        )
        session = SgRequests()
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
    website = "dairyqueen.ca"
    typ = "<MISSING>"
    country = "CA"
    for loc in locs:
        PFound = False
        count = 0
        while PFound is False:
            count = count + 1
            loc = loc + "/"
            loc = loc.replace("https://", "HTTPS")
            loc = loc.replace("//", "/")
            loc = loc.replace("HTTPS", "https://")
            Closed = False
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = loc.rsplit("/", 2)[1]
            phone = ""
            lat = ""
            lng = ""
            hours = ""
            session = SgRequests()
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "this page doesn't exist" in line2:
                    Closed = True
                if '<h1 class="my-1 h2">' in line2:
                    name = line2.split('<h1 class="my-1 h2">')[1].split("<")[0]
                if '"address3":"' in line2:
                    add = line2.split('"address3":"')[1].split('"')[0]
                    PFound = True
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
                if '"miniSite":{"miniSiteHours":"' in line2:
                    days = (
                        line2.split('"miniSite":{"miniSiteHours":"')[1]
                        .split('","')[0]
                        .split(",")
                    )
                    for day in days:
                        dnum = day.split(":")[0]
                        if dnum == "1":
                            hrs = "Sunday: " + day.split(":", 1)[1]
                        if dnum == "2":
                            hrs = "Monday: " + day.split(":", 1)[1]
                        if dnum == "3":
                            hrs = "Tuesday: " + day.split(":", 1)[1]
                        if dnum == "4":
                            hrs = "Wednesday: " + day.split(":", 1)[1]
                        if dnum == "5":
                            hrs = "Thursday: " + day.split(":", 1)[1]
                        if dnum == "6":
                            hrs = "Friday: " + day.split(":", 1)[1]
                        if dnum == "7":
                            hrs = "Saturday: " + day.split(":", 1)[1]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&amp;", "&").replace("&amp", "&")
            add = add.replace("&amp;", "&").replace("&amp", "&")
            add = add.replace("\\u0026", "&")
            if Closed is False:
                city = city.replace("\\u0026apos;", "'")
                add = add.replace("\\u0026apos;", "'")
                name = name.replace("\\u0026apos;", "'")
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
            if count >= 3:
                PFound = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
