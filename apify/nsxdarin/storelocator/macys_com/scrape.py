from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("macys_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://l.macys.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://l.macys.com/" in line and ".html" not in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            if lurl.count("/") == 3:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "macys.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        hours = ""
        country = "US"
        city = ""
        add = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        phone = ""
        store = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if name == "" and '<span class="LocationName-geo">' in line2:
                name = (
                    "Macy's "
                    + line2.split('<span class="LocationName-geo">')[1].split("<")[0]
                )
            if '"address":' in line2:
                add = line2.split('"line1":"')[1].split('"')[0]
                try:
                    add = add + " " + line2.split('"line2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"region":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
            if phone == "" and '<meta itemprop="telephone" content="' in line2:
                phone = (
                    line2.split('<meta itemprop="telephone" content="')[1]
                    .split('"')[0]
                    .replace("+", "")
                )
            if hours == "" and "data-days='[" in line2:
                days = line2.split("data-days='[")[1].split(']},"')[0].split('"day":"')
                for day in days:
                    if "isClosed" in day:
                        if 'isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            dstart = day.split('"start":')[1].split("}")[0]
                            dend = day.split('"end":')[1].split("}")[0]
                            if len(dstart) == 3:
                                dstart = dstart[:1] + ":" + dstart[-2:]
                            else:
                                dstart = dstart[:2] + ":" + dstart[-2:]
                            if len(dend) == 3:
                                dend = dend[:1] + ":" + dend[-2:]
                            else:
                                dend = dend[:2] + ":" + dend[-2:]
                            hrs = day.split('"')[0] + ": " + dstart + "-" + dend
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if 'entityType":"location","id":"' in line2:
                store = line2.split('entityType":"location","id":"')[1].split('"')[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
            if '<meta itemprop="longitude" content="' in line2:
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        name = name.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
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
