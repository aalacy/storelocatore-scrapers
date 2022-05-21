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

logger = SgLogSetup().get_logger("juliancharles_co_uk")


def fetch_data():
    url = "https://www.juliancharles.co.uk/store-finder"
    r = session.get(url, headers=headers)
    website = "juliancharles.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "name: '" in line:
            name = line.split("name: '")[1].split("'")[0]
            addinfo = line.split("address: '")[1].split("'")[0]
            phone = line.split("phone: '")[1].split("'")[0]
            lat = line.split("{lat: ")[1].split(",")[0]
            lng = line.split("lng: ")[1].split("}")[0]
            hours = (
                line.split("}, ")[1].split("},")[0].replace("'", "").replace(", ", "; ")
            )
            store = "<MISSING>"
            state = "<MISSING>"
            loc = "https://www.juliancharles.co.uk/store-finder"
            if addinfo.count(",") == 5:
                add = (
                    addinfo.split(",")[1].strip()
                    + " "
                    + addinfo.split(",")[2].strip()
                    + " "
                    + addinfo.split(",")[3].strip()
                )
                city = addinfo.split(",")[4].strip()
                zc = addinfo.split(",")[5].strip()
            elif addinfo.count(",") == 4:
                add = (
                    addinfo.split(",")[1].strip() + " " + addinfo.split(",")[2].strip()
                )
                city = addinfo.split(",")[3].strip()
                zc = addinfo.split(",")[4].strip()
            elif addinfo.count(",") == 3:
                add = addinfo.split(",")[1].strip()
                city = addinfo.split(",")[2].strip()
                zc = addinfo.split(",")[3].strip()
            else:
                add = addinfo.split(",")[0].strip()
                city = addinfo.split(",")[1].strip()
                zc = addinfo.split(",")[2].strip()
            if "Bideford" in city:
                city = "Bideford"
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
