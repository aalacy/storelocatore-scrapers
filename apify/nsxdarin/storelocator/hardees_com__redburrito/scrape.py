from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("hardees_com__redburrito")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://hardees.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "hardees.com"
    for line in r.iter_lines():
        if "<loc>https://locations.hardees.com/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0].replace("--", "-"))
    for loc in locs:
        try:
            if "fort-smith/1820-phoenix" in loc:
                loc = "https://locations.hardees.com/ar/fort-smith/1820-phoenix-ave"
            logger.info(loc)
            country = "US"
            typ = "<MISSING>"
            name = ""
            add = ""
            city = ""
            state = ""
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
                    if ":" in name:
                        name = name.split(":")[0].strip()
                if '<meta itemprop="streetAddress" content="' in line2:
                    add = line2.split('<meta itemprop="streetAddress" content="')[
                        1
                    ].split("<")[0]
                if '<span class="location-address">' in line2:
                    csz = line2.split('<span class="location-address">')[1].split("<")[
                        0
                    ]
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().split(" ")[0]
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
                        line2.strip()
                        .replace("\t", "")
                        .replace("\r", "")
                        .replace("\n", "")
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
                if "Red Burrito</span>" in line2:
                    RB = True
            if RB is True:
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
