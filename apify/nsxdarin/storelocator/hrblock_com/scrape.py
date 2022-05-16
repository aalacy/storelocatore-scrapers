from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("hrblock_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.hrblock.com/tax-offices/local/"
    alllocs = []
    states = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a href="https://www.hrblock.com/tax-offices/local/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            states.append(lurl)
    for state in states:
        logger.info("Pulling State %s..." % state)
        cities = []
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if (
                '<a class="right-arrow" href="https://www.hrblock.com/tax-offices/local/'
                in line2
            ):
                lurl = line2.split('<a class="right-arrow" href="')[1].split('"')[0]
                cities.append(lurl)
        for city in cities:
            logger.info("Pulling City %s..." % city)
            r3 = session.get(city, headers=headers)
            for line3 in r3.iter_lines():
                if ">View office" in line3:
                    lurl = (
                        "https://www.hrblock.com/local-tax-offices/"
                        + line3.split("local-tax-offices/")[1].split('"')[0]
                    )
                    if "www.blockadvisors.com" in lurl:
                        lurl = lurl.replace("https://hrblock.com", "")
                    if lurl not in alllocs:
                        alllocs.append(lurl)
                        logger.info("Pulling Location %s..." % lurl)
                        try:
                            r4 = session.get(lurl, headers=headers)
                            lines = r4.iter_lines()
                            website = "hrblock.com"
                            typ = "Location"
                            name = "H&R Block"
                            store = lurl.rsplit("/", 1)[1]
                            hours = "<MISSING>"
                            add = ""
                            city = ""
                            country = "US"
                            state = ""
                            zc = ""
                            phone = ""
                            lat = ""
                            lng = ""
                            for line4 in lines:
                                if '<span itemprop="streetAddress">' in line4:
                                    if add == "":
                                        add = line4.split(
                                            '<span itemprop="streetAddress">'
                                        )[1].split("<")[0]
                                    else:
                                        add = (
                                            add
                                            + " "
                                            + line4.split(
                                                '<span itemprop="streetAddress">'
                                            )[1].split("<")[0]
                                        )
                                if '<span itemprop="addressLocality">' in line4:
                                    city = line4.split(
                                        '<span itemprop="addressLocality">'
                                    )[1].split("<")[0]
                                if '<span itemprop="addressRegion">' in line4:
                                    state = line4.split(
                                        '<span itemprop="addressRegion">'
                                    )[1].split("<")[0]
                                if '<span itemprop="postalCode">' in line4:
                                    zc = line4.split('<span itemprop="postalCode">')[
                                        1
                                    ].split("<")[0]
                                if '<a href="tel:' in line4:
                                    phone = line4.split('<a href="tel:')[1].split('"')[
                                        0
                                    ]
                                if 'itemprop="latitude"' in line4:
                                    lat = line4.split('content="')[1].split('"')[0]
                                if 'itemprop="longitude"' in line4:
                                    lng = line4.split('content="')[1].split('"')[0]
                            if lat == "":
                                lat = "<MISSING>"
                            if lng == "":
                                lng = "<MISSING>"
                            if add != "":
                                city = city.replace(",", "")
                                yield SgRecord(
                                    locator_domain=website,
                                    page_url=lurl,
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
