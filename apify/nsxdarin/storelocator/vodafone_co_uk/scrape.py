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

logger = SgLogSetup().get_logger("vodafone_co_uk")


def fetch_data():
    url = "https://www.vodafone.co.uk/help-and-information/store-locator"
    r = session.get(url, headers=headers)
    website = "vodafone.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "https://www.vodafone.co.uk/help-and-information/store-locator"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if 'CMSStoreLocator_":{"jsonData":"' in line:
            items = line.split("storecode")
            for item in items:
                if "eshoptown" in item:
                    phone = "<MISSING>"
                    store = item.split('\\": \\"')[1].split("\\")[0]
                    name = item.split('"name\\": \\"')[1].split('\\",')[0].strip()
                    city = item.split('eshoptown\\": \\"')[1].split('\\"')[0].strip()
                    state = "<MISSING>"
                    zc = item.split('"postcode\\": \\"')[1].split("\\")[0].strip()
                    lat = item.split('"lat\\": \\"')[1].split("\\")[0].strip()
                    lng = item.split('"lng\\": \\"')[1].split("\\")[0].strip()
                    hours = item.split('"hours\\": \\"')[1].split('\\"')[0].strip()
                    if "Store Mobile:" in hours:
                        phone = hours.split("Store Mobile:")[1].strip()
                    if ", Store" in hours:
                        hours = hours.split(", Store")[0].strip()
                    add = item.split('"address\\": \\"')[1].split('\\",')[0]
                    add = (
                        add.replace("  ", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                        .replace(" ,", ",")
                    )
                    ctext = ", " + city
                    if ctext in add:
                        add = add.rsplit(ctext, 1)[0].strip()
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
