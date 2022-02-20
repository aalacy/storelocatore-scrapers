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

logger = SgLogSetup().get_logger("walmart_com__cp__care-clinics__1224932")


def fetch_data():
    url = "https://www.walmart.com/cp/care-clinics/1224932"
    r = session.get(url, headers=headers)
    website = "walmart.com/cp/care-clinics/1224932"
    typ = "Care Clinic"
    country = "US"
    loc = "<MISSING>"
    hours = ""
    lat = "<MISSING>"
    lng = "<MISSING>"
    sid = 0
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = (
            line.replace("%20", " ")
            .replace("%3E", ">")
            .replace("%2F", "/")
            .replace("%2C", ",")
            .replace("%3C", "<")
            .replace("%3D", "=")
        )
        if "Illinois" in line:
            items = line.split("'text'%3A'Health Center locations'")[1].split(
                "%5Cn  <li>"
            )
            for item in items:
                if "%26nbsp%3B%26nbsp%3B%26nbsp%" in item or "479-306-7484" in item:
                    sid = sid + 1
                    name = "Walmart Care Clinic"
                    if "479-306-7484" in item:
                        addinfo = (
                            item.split("479-306-7484")[0].strip().replace("\t", "")
                        )
                    else:
                        addinfo = (
                            item.split("%26nbsp%3B%26nbsp%3B%26nbsp%")[0]
                            .strip()
                            .replace("\t", "")
                        )
                    addinfo = addinfo.replace("AR, ", "AR ").replace("  ", " ")
                    addinfo = (
                        addinfo.replace("%23200", ",")
                        .replace(" , ", ", ")
                        .replace("%26nbsp%3B", " ")
                        .strip()
                    )
                    zc = addinfo.rsplit(" ", 1)[1]
                    state = addinfo.rsplit(" ", 2)[1]
                    if "GA" in state:
                        state = "GA"
                    add = addinfo.split(",")[0]
                    city = addinfo.rsplit(" ", 3)[1]
                    if "479-306-7484" in item:
                        phone = "479-306-7484"
                    else:
                        phone = item.rsplit("%3B%26nbsp%3B", 1)[1].split("<")[0]
                    if state == "AR":
                        hours = (
                            "Monday-Saturday 7:30 am-7:30 pm and Sunday 10 am - 6 pm"
                        )
                    if state == "GA":
                        hours = (
                            "Monday-Saturday 7:30 am-7:30 pm and Sunday 10 am - 6 pm"
                        )
                    if state == "IL":
                        hours = (
                            "Monday-Saturday 7:30 am-6:00 pm and Sunday 10 am - 6 pm"
                        )
                    if state == "TX":
                        hours = "M-F: 8am-8pm, Sat: 8am-5pm, Sun: 10am-6pm"
                    add = add.replace(city, "").strip()
                    if "4870 Elm" in add:
                        add = add + " Suite B"
                    if "4221 Atlanta" in add:
                        add = add + " Suite 101"
                        city = "Loganville"
                        state = "GA"
                        zc = "30052"
                    if "494 W" in add:
                        city = "Royse City"
                    if "6020 Harrison Rd" in add:
                        phone = "478-703-0468"
                        city = "Macon"
                    if "5448 Whittlesey Blvd" in add:
                        city = "Columbus"
                    if "  GA" in add:
                        add = add.split("  GA")[0]
                    if "  IL" in add:
                        add = add.split("  IL")[0]
                    if "  TX" in add:
                        add = add.split("  TX")[0]
                    store = str(sid)
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
