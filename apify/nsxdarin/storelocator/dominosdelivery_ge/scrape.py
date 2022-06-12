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

logger = SgLogSetup().get_logger("dominosdelivery_ge")


def fetch_data():
    url = "https://dominosdelivery.ge/locations"
    r = session.get(url, headers=headers)
    website = "dominosdelivery.ge"
    typ = "<MISSING>"
    country = "GE"
    loc = "<MISSING>"
    coords = []
    zc = "<MISSING>"
    state = "<MISSING>"
    name = "<MISSING>"
    phone = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    places = []
    lines = r.iter_lines()
    for line in lines:
        if '["<center>' in line:
            coords.append(
                line.split(",</br>")[1].split("<")[0].strip()
                + "|"
                + line.split('", ')[1].split(",")[0]
                + "|"
                + line.split('", ')[1].split(",")[1].strip().split("]")[0]
            )
        if "<h3>" in line:
            pname = line.split("<h3>")[1].split("<")[0]
            g = next(lines)
            h = next(lines)
            padd = g.split(">")[1].split("<")[0]
            phours = h.split(": ")[1].split("<")[0].strip()
            pcity = name
            places.append(pname + "|" + padd + "|" + pcity + "|" + phours)
        for item in coords:
            for place in places:
                if item.split("|")[0] == place.split("|")[1]:
                    lat = item.split("|")[1]
                    lng = item.split("|")[2]
                    name = place.split("|")[0]
                    add = place.split("|")[1]
                    city = place.split("|")[2]
                    hours = place.split("|")[3]
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
