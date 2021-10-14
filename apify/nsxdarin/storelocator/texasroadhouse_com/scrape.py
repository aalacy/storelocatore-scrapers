from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("texasroadhouse_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.texasroadhouse.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.texasroadhouse.com/locations/" in line:
            lurl = line.split("<loc>")[1].split("<")[0]
            locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        name = ""
        add = ""
        website = "texasroadhouse.com"
        country = "<MISSING>"
        add = ""
        store = "<MISSING>"
        city = ""
        typ = "<MISSING>"
        state = "<MISSING>"
        zc = ""
        lat = ""
        lng = ""
        phone = ""
        hours = ""
        for line2 in r2.iter_lines():
            if 'itemprop="name">' in line2:
                name = line2.split('itemprop="name">')[1].split("<")[0]
            if '"address1":"' in line2:
                add = line2.split('"address1":"')[1].split('"')[0]
                try:
                    city = line2.split('"city":"')[1].split('"')[0]
                except:
                    city = "<MISSING>"
                try:
                    state = line2.split('"state":"')[1].split('"')[0]
                except:
                    pass
                country = line2.split('"countryCode":"')[1].split('"')[0]
                try:
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                except:
                    zc = "<MISSING>"
                try:
                    phone = line2.split('"telephone":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split(',"longitude":')[1].split(",")[0]
                days = line2.split('"schedule":[')[1].split("]")[0].split('"day":"')
                for day in days:
                    if '"hours":' in day:

                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"openTime":"')[1].split('"')[0]
                            + "-"
                            + day.split('"closeTime":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if add != "" and city != "<MISSING>":
            name = name.replace("\\u0027", "'")
            add = add.replace("\\u0027", "'")
            name = name.replace("\\/", "/")
            add = add.replace("\\/", "/")
            if lat == "0":
                lat = "<MISSING>"
            if lng == "0":
                lng = "<MISSING>"
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
