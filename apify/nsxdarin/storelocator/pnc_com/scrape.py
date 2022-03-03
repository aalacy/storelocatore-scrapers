from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("pnc_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-frame-options": "ALLOW-FROM https://www.apply2.pnc.com/",
    "x-xss-protection": "1; mode=block",
    "x-ua-compatible": "IE=Edge",
    "strict-transport-security": "max-age=31536000",
    "authority": "apps.pnc.com",
    "method": "GET",
    "scheme": "https",
    "accept": "application/json, text/plain, */*",
    "x-app-key": "pyHnMuBXUM1p4AovfkjYraAJp6",
    "content-encoding": "gzip",
}

headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = (
        "https://apps.pnc.com/locator-api/locator/api/v1/locator/browse?t=1578513813794"
    )
    session = SgRequests()
    r = session.get(url, headers=headers)
    locs = []
    for line in [str(x) for x in r.iter_lines()]:
        if '"externalId" : "' in line:
            lid = line.split('" : "')[1].split('"')[0]
            locs.append(lid)
    logger.info(("Found %s Locations..." % str(len(locs))))
    i = 0
    for loc in locs:
        i += 1
        if i % 30 == 0:
            session = SgRequests()
        lurl = "https://apps.pnc.com/locator-api/locator/api/v2/location/" + loc
        logger.info(("Pulling Location %s..." % loc))
        try:
            r2 = session.get(lurl, headers=headers2)
            lines = (str(x) for x in r2.iter_lines())
            website = "pnc.com"
            HFound = False
            hours = ""
            TypFound = False
            for line2 in lines:
                if '"locationName" : "' in line2:
                    name = line2.split('"locationName" : "')[1].split('"')[0]
                if '"locationTypeDesc" : "' in line2 and TypFound is False:
                    TypFound = True
                    typ = line2.split('"locationTypeDesc" : "')[1].split('"')[0]
                    store = loc
                if '"address1" : "' in line2:
                    add = line2.split('"address1" : "')[1].split('"')[0]
                if '"address2" : "' in line2:
                    add = add + " " + line2.split('"address2" : "')[1].split('"')[0]
                if '"city" : "' in line2:
                    city = line2.split('"city" : "')[1].split('"')[0]
                if '"state" : "' in line2:
                    state = line2.split('"state" : "')[1].split('"')[0]
                if '"zip" : "' in line2:
                    zc = line2.split('"zip" : "')[1].split('"')[0]
                if '"latitude" : ' in line2:
                    lat = line2.split('"latitude" : ')[1].split(",")[0]
                if '"longitude" : ' in line2:
                    lng = line2.split('"longitude" : ')[1].split(",")[0]
                if '"contactDescriptionDB" : "External Phone",' in line2:
                    phone = next(lines).split(' : "')[1].split('"')[0]
                if '"serviceNameDB" : "Lobby Hours"' in line2:
                    HFound = True
                if HFound and '"hoursByDayIndex"' in line2:
                    HFound = False
                if HFound and 'day"' in line2:
                    day = line2.split('"')[1]
                    g = next(lines)
                    h = next(lines)
                    if "null" in g:
                        hrs = "Closed"
                    else:
                        hrs = g.split('"')[3] + "-" + h.split('"')[3]
                    if hours == "":
                        hours = day + ": " + hrs
                    else:
                        hours = hours + "; " + day + ": " + hrs
            country = "US"
            purl = "https://apps.pnc.com/locator/#/result-details/" + loc
            if hours == "":
                hours = "<MISSING>"
            purl = purl + "/" + name.replace("#", "").replace(" ", "-").lower()
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
