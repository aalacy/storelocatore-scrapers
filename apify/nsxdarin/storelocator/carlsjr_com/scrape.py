from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("carlsjr_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    canada = ["AB", "BC", "SK", "QC", "PEI"]
    australia = ["NSW", "SA", "QLD", "VIC"]
    mexico = ["BCS", "COAH", "HGO", "JAL", "PUE", "QROO", "SIN", "YUC"]
    url = "https://carlsjr.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "carlsjr.com"
    for line in r.iter_lines():
        if "<loc>https://carlsjr.com/locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        time.sleep(6)
        logger.info(loc)
        country = "US"
        typ = "<MISSING>"
        name = ""
        add = ""
        city = ""
        if "/intl/" in loc:
            state = loc.split("/locations/intl/")[1].split("/")[0].upper()
        else:
            state = loc.split("/locations/")[1].split("/")[0].upper()
        zc = ""
        phone = ""
        lat = ""
        store = "<MISSING>"
        lng = ""
        hours = ""
        RB = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                add = name
            if '<span class="location-address">' in line2:
                csz = (
                    line2.split('<span class="location-address">')[1]
                    .split("<")[0]
                    .strip()
                )
                if csz.count(",") == 1:
                    city = csz.split(",")[0]
                else:
                    city = csz.split(",")[1]
                if state in canada:
                    zc = csz.rsplit(" ", 2)[1] + " " + csz.rsplit(" ", 1)[1]
                else:
                    zc = csz.rsplit(" ", 1)[1]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "lat: " in line2:
                lat = line2.split("lat: ")[1].split(",")[0]
            if "lng: " in line2:
                lng = (
                    line2.split("lng: ")[1]
                    .strip()
                    .replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                )
            if "<li><span>Mon" in line2:
                hours = (
                    line2.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                )
                hours = hours.replace("</span></li><li><span>", "; ").replace(
                    " <span></span> ", "-"
                )
                hours = (
                    hours.replace("<li>", "")
                    .replace("</li>", "")
                    .replace("<span>", "")
                    .replace("</span>", "")
                )
            if "Green Burrito</span>" in line2:
                RB = True
        if state.upper() in mexico:
            country = "MX"
        if state.upper() in australia:
            country = "AU"
        if state.upper() in canada:
            country = "CA"
        if "-spain" in state.lower():
            country = "ES"
            state = "<MISSING>"
        if "-thailand" in state.lower():
            country = "TH"
            state = "<MISSING>"
        if "jakarta" in state.lower():
            country = "ID"
            state = "<MISSING>"
        if "singapore" in state.lower():
            country = "SG"
            state = "<MISSING>"
        if phone.strip() == "0" or len(phone) <= 5:
            phone = "<MISSING>"
        if (
            "1" not in phone
            and "2" not in phone
            and "3" not in phone
            and "4" not in phone
            and "5" not in phone
            and "6" not in phone
            and "7" not in phone
            and "8" not in phone
        ):
            phone = "<MISSING>"
        if RB is False:
            if add != "":
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
