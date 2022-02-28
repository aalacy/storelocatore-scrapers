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

logger = SgLogSetup().get_logger("ilovedirtcheap_com")


def fetch_data():
    locs = []
    url = "https://ilovedirtcheap.com/locations/"
    r = session.get(url, headers=headers)
    website = "ilovedirtcheap.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<div class='buttons'><a href='" in line:
            locs.append(line.split("<div class='buttons'><a href='")[1].split("'")[0])
    for loc in locs:
        logger.info(loc)
        HFound = False
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        store = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if "LatLng(" in line2:
                lat = line2.split("LatLng(")[1].split(",")[0]
                lng = line2.split("LatLng(")[1].split(",")[1].split(")")[0]
            if "<p class='address'>" in line2:
                add = line2.split("<p class='address'>")[1].split("<")[0]
                city = line2.split("<br/>")[1].split(",")[0]
                state = line2.split("<br/>")[1].split(",")[1].strip().split(" ")[0]
                zc = line2.split("<br/>")[1].rsplit(" ", 1)[1]
                phone = line2.split("<br/>")[2].split("<")[0]
            if "https://app.dirtcheapalerts.com/api/get_website_alerts/" in line2:
                store = line2.split(
                    "https://app.dirtcheapalerts.com/api/get_website_alerts/"
                )[1].split("/")[0]
            if "Hours</h3>" in line2:
                HFound = True
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and "<br />" in line2:
                hrs = line2.replace("<p>", "").replace("</p>", "").split("<")[0]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if HFound and "pm<" in line2 and "<br />" not in line2:
                hrs = (
                    line2.replace("<p>", "")
                    .replace("</p>", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("\n", "")
                    .strip()
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if "dirt-cheap-corporate-office" in loc:
            hours = "9am-8pm, Mon-Sat; 12pm-7pm Sunday"
        hours = hours.replace("\t", "").strip()
        if "; Thanks" in hours:
            hours = hours.split("; Thanks")[0].strip()
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
