from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("ae_com__outlet")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://storelocations.ae.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if (
            "<loc>https://storelocations.ae.com/ca/" in line
            or "<loc>https://storelocations.ae.com/us/" in line
        ):
            lurl = line.split(">")[1].split("<")[0]
            count = lurl.count("/")
            if count == 6:
                locs.append(lurl)
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "ae.com/outlet"
        typ = ""
        hours = ""
        phone = ""
        name = ""
        lat = ""
        lng = ""
        city = ""
        store = ""
        state = ""
        zc = ""
        if ".com/ca/" in loc:
            country = "CA"
        else:
            country = "US"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace("&amp;", "&")
            if "days='[" in line2:
                days = line2.split("days='[")[1].split("]}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        dname = day.split('"')[0]
                        try:
                            hrs = (
                                day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                            if hours == "":
                                hours = dname + ": " + hrs
                            else:
                                hours = hours + "; " + dname + ": " + hrs
                        except:
                            hours = "CLOSED"
            if 'itemprop="address" data-country="' in line2:
                city = line2.split('<meta itemprop="addressLocality" content="')[
                    1
                ].split('"')[0]
                add = line2.split('"streetAddress" content="')[1].split('"')[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                lat = line2.split('data-lat="')[1].split('"')[0]
                lng = line2.split('data-long="')[1].split('"')[0]
                try:
                    phone = line2.split('data-ya-track="phone">')[1].split("<")[0]
                except:
                    phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if typ == "":
            typ = "American Eagle"
        store = "<MISSING>"
        if city != "" and hours != "CLOSED" and " outlet" in name.lower():
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
