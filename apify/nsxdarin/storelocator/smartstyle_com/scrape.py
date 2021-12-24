from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("smartstyle_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.smartstyle.com/en-us/salon-directory.html"
    locs = []
    canada = ["ab", "nb", "on", "bc", "nl", "qc", "mb", "ns", "sk"]
    states = []
    donelocs = []
    session = SgRequests()
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'style="width: 100%; margin-bottom: 10px;" href="' in line:
            states.append(line.split('href="')[1].split('"')[0])
    for state in states:
        try:
            logger.info("Pulling State %s..." % state)
            r2 = session.get(state, headers=headers)
            for line2 in r2.iter_lines():
                if '<tr><td><a href="' in line2:
                    locs.append(
                        "https://www.smartstyle.com"
                        + line2.split('href="')[1].split('"')[0]
                    )
        except:
            pass
    logger.info("Found %s Locations." % str(len(locs)))
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        store = loc.split(".html")[0].rsplit("-", 1)[1]
        lat = ""
        lng = ""
        hours = ""
        country = "US"
        zc = ""
        phone = ""
        logger.info("Pulling Location %s..." % loc)
        website = "smartstyle.com"
        typ = "Salon"
        PFound = True
        retries = 0
        while PFound:
            try:
                time.sleep(10)
                PFound = False
                retries = retries + 1
                session = SgRequests()
                dcount = 0
                r2 = session.get(loc, headers=headers, timeout=5)
                for line2 in r2.iter_lines():
                    if '<meta itemprop="openingHours" content="' in line2:
                        dcount = dcount + 1
                        hrs = (
                            line2.split('<meta itemprop="openingHours" content="')[1]
                            .split('"')[0]
                            .strip()
                        )
                        if dcount <= 7:
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if '<h2 class="hidden-xs salontitle_salonlrgtxt">' in line2:
                        name = line2.split(
                            '<h2 class="hidden-xs salontitle_salonlrgtxt">'
                        )[1].split("<")[0]
                    if 'var salonDetailLat = "' in line2:
                        lat = line2.split('var salonDetailLat = "')[1].split('"')[0]
                    if 'var salonDetailLng = "' in line2:
                        lng = line2.split('var salonDetailLng = "')[1].split('"')[0]
                    if 'itemprop="streetAddress">' in line2:
                        add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                    if '<span  itemprop="addressLocality">' in line2:
                        city = line2.split('<span  itemprop="addressLocality">')[
                            1
                        ].split("<")[0]
                    if '<span itemprop="addressRegion">' in line2:
                        state = line2.split('<span itemprop="addressRegion">')[1].split(
                            "<"
                        )[0]
                    if '"postalCode">' in line2:
                        zc = line2.split('"postalCode">')[1].split("<")[0]
                    if 'id="sdp-phn" value="' in line2:
                        phone = line2.split('id="sdp-phn" value="')[1].split('"')[0]
                    if (
                        "sc_secondLevel = '/content/smartstyle/www/en-us/locations/"
                        in line2
                    ):
                        stabb = line2.split(
                            "sc_secondLevel = '/content/smartstyle/www/en-us/locations/"
                        )[1].split("'")[0]
                if stabb in canada:
                    country = "CA"
                if add != "":
                    if phone == "":
                        phone = "<MISSING>"
                    if hours == "":
                        hours = "<MISSING>"
                    state = state.replace("&nbsp;", "")
                    if loc not in donelocs:
                        donelocs.append(loc)
                        if "0" not in hours and "3" not in hours and "1" not in hours:
                            hours = "Sun-Sat: Closed"
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
                if retries <= 10:
                    PFound = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
