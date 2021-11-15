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

logger = SgLogSetup().get_logger("zaxbys_com")


def fetch_data():
    locs = []
    url = "https://www.zaxbys.com/sitemap.xml"
    r = session.get(url, headers=headers)
    website = "zaxbys.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "<loc>https://www.zaxbys.com/locations/" in line:
            items = line.split("<loc>https://www.zaxbys.com/locations/")
            for item in items:
                if "<xmp><urlset" not in item:
                    locs.append(
                        "https://www.zaxbys.com/locations/" + item.split("<")[0]
                    )
    for loc in locs:
        if loc != "https://www.zaxbys.com/locations/":
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
            hours = ""
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "&q;Address&q;:&q;" in line2:
                    add = line2.split("&q;Address&q;:&q;")[1].split("&q;")[0]
                    city = line2.split("&q;City&q;:&q;")[1].split("&q")[0]
                    state = line2.split("&q;State&q;:&q;")[1].split("&q")[0]
                    zc = line2.split("Zip&q;:&q;")[1].split("&q")[0]
                    lat = line2.split("Latitude&q;:&q;")[1].split("&")[0]
                    lng = line2.split("Longitude&q;:&q;")[1].split("&")[0]
                    phone = line2.split("&q;Phone&q;:&q;")[1].split("&")[0]
                    hrs = line2.split("toreHours&q;:&q;")[1].split(";&q;")[0]
                    hours = hrs.replace(";7,", "; Sunday: ")
                    hours = hours.replace(";6,", "; Saturday: ")
                    hours = hours.replace(";5,", "; Friday: ")
                    hours = hours.replace(";4,", "; Thursday: ")
                    hours = hours.replace(";3,", "; Wednesday: ")
                    hours = hours.replace(";2,", "; Tuesday: ")
                    hours = hours.replace("1,", "Monday: ")
                    hours = hours.replace(",", "-")
                    name = add
            if "ae/quebec/" in loc:
                country = "CA"
            if city != "" and "q;Website&" not in hours:
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
