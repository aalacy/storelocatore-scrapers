from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("tacobell_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    locs = []
    url = "https://www.tacobell.ca/en/stores/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<script id="all_stores_locations"' in line:
            items = line.split('"slug": "')
            for item in items:
                if '<script id="all_stores_locations"' not in item:
                    sid = item.split('"')[0]
                    lat = item.split('"latitude": ')[1].split(",")[0]
                    lng = item.split('"longitude": ')[1].split(",")[0]
                    lurl = "https://www.tacobell.ca/en/store/" + sid
                    locs.append(lurl + "|" + lat + "|" + lng)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        website = "tacobell.ca"
        typ = "Restaurant"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "CA"
        store = "<MISSING>"
        phone = ""
        hours = ""
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        name = "Taco Bell"
        r2 = session.get(loc.split("|")[0], headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '<h1 class="store-location-title">' in line2:
                add = line2.split('<h1 class="store-location-title">')[1].split("<")[0]
                cs = line2.split('<p class="text">')[1].split("<")[0]
                state = cs.split(",")[1].strip()
                city = cs.split(",")[0].strip()
                zc = "<MISSING>"
            if "<tr><td>" in line2:
                days = line2.split("<tr><td>")
                for day in days:
                    if "Closed</th>" not in day:
                        hrs = (
                            day.split("<")[0]
                            + ": "
                            + day.split("</td><td>")[1]
                            + "-"
                            + day.split("</td><td>")[2].split("<")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        add = add.replace("&#x27;", "'")
        yield SgRecord(
            locator_domain=website,
            page_url=loc.split("|")[0],
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
