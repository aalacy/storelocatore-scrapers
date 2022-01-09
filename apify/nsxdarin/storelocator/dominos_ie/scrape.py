from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_ie")


def fetch_data():
    url = "https://www.dominos.ie/pizza-near-me/sitemap.xml"
    r = session.get(url, headers=headers)
    locs = []
    website = "dominos.ie"
    typ = "<MISSING>"
    country = "IE"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.dominos.ie/pizza-near-me/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 5:
                locs.append(lurl)
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        phone = ""
        zc = "<MISSING>"
        store = "<MISSING>"
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if hours == "" and "data-days='[{" in line2:
                days = (
                    line2.split("data-days='[{")[1]
                    .split("' data-utc-")[0]
                    .split('"day":"')
                )
                for day in days:
                    if "intervals" in day:
                        if 'isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split(',"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if phone == "" and 'itemprop="telephone">' in line2:
                phone = line2.split('itemprop="telephone">')[1].split("<")[0].strip()
            if lat == "" and '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if '<span class="Core-geo">' in line2:
                name = line2.split('<span class="Core-geo">')[1].split("<")[0]
            if add == "" and '"Address-field Address-line1">' in line2:
                add = line2.split('"Address-field Address-line1">')[1].split("<")[0]
                city = line2.split('"Address-field Address-city">')[1].split("<")[0]
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
