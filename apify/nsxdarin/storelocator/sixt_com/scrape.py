from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()

logger = SgLogSetup().get_logger("sixt_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.sixt.com/mount/xml-sitemaps/branches.xml"
    r = session.get(url, headers=headers)
    website = "sixt.com"
    typ = "<MISSING>"
    country = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "loc>https://www.sixt.com/car-rental/" in line:
            items = line.split("loc>https://www.sixt.com/car-rental/")
            for item in items:
                if "xml version" not in item:
                    lurl = "https://www.sixt.com/car-rental/" + item.split("<")[0]
                    locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "title: '" in line2:
                name = line2.split("title: '")[1].split("'")[0]
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
                country = line2.split('addressRegion":"')[1].split('"')[0]
            if "<h2>Sixt Services" in line2:
                htext = line2.split("<h2>Sixt Services")[1].split("<")[0]
                if "," in htext:
                    state = htext.split(",")[1].strip()
                else:
                    state = "<MISSING>"
            if '"openingHours":[' in line2:
                hours = line2.split('"openingHours":[')[1].split('"]')[0]
                hours = hours.replace('"24-hour return","', "")
                if '","HOLIDAYS' in hours:
                    hours = hours.split('","HOLIDAYS')[0]
                hours = hours.replace('","', "; ")
                hours = hours.replace('"', "")
        if state == "":
            state = "<MISSING>"
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
