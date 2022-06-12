from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("aramarkuniform_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.108 Safari/537.36"
}


def fetch_data():
    locs = []
    allstates = [
        "AL",
        "AK",
        "AZ",
        "AR",
        "CA",
        "CO",
        "CT",
        "DE",
        "DC",
        "FL",
        "GA",
        "HI",
        "ID",
        "IL",
        "IN",
        "IA",
        "KS",
        "KY",
        "LA",
        "ME",
        "MD",
        "MA",
        "MI",
        "MN",
        "MS",
        "MO",
        "MT",
        "NE",
        "NV",
        "NH",
        "NJ",
        "NM",
        "NY",
        "NC",
        "ND",
        "OH",
        "OK",
        "ON",
        "OR",
        "PA",
        "PR",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UT",
        "VT",
        "VA",
        "WA",
        "WV",
        "WI",
        "WY",
    ]
    url = "https://www.aramarkuniform.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<url><loc>https://www.aramarkuniform.com/our-locations/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for stateabb in allstates:
        logger.info(("Pulling State %s..." % stateabb))
        url = (
            "https://www.aramarkuniform.com/ausgetlocations?zip=&city=&state="
            + stateabb
        )
        r2 = session.post(url, headers=headers)
        lines = r2.iter_lines()
        website = "aramarkuniform.com"
        for line2 in lines:
            if '"url":"' in line2:
                items = line2.split('"url":"')
                for item in items:
                    if '{"total' not in item:
                        lurl = (
                            "https://www.aramarkuniform.com"
                            + item.split('"')[0].split("?")[0]
                        )
                        if lurl not in locs:
                            locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'data-pin="' in line2:
                name = line2.split('data-pin="')[1].split('"')[0]
                if " | " in name:
                    typ = name.split(" | ")[1]
                    name = name.split(" | ")[0]
            if 'latitude" content="' in line2:
                lat = line2.split('latitude" content="')[1].split('"')[0]
            if '"longitude" content="' in line2:
                lng = line2.split('"longitude" content="')[1].split('"')[0]
            if 'itemprop="streetAddress">' in line2:
                add = (
                    line2.split('itemprop="streetAddress">')[1]
                    .split("<")[0]
                    .replace("&amp;", "&")
                )
            if 'itemprop="addressLocality">' in line2:
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
            if 'itemprop="addressRegion">' in line2:
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
            if 'itemprop="postalCode">' in line2:
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
        canada = [
            "SK",
            "AB",
            "BC",
            "ON",
            "NT",
            "PEI",
            "PE",
            "QC",
            "NS",
            "NF",
            "NL",
        ]
        if state in canada:
            country = "CA"
        else:
            country = "US"
        if phone == "":
            phone = "<MISSING>"
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
