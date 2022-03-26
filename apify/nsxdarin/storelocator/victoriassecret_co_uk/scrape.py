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

logger = SgLogSetup().get_logger("victoriassecret_co_uk")


def fetch_data():
    url = "https://www.victoriassecret.co.uk/store-locator"
    r = session.get(url, headers=headers)
    website = "victoriassecret.co.uk"
    typ = "<MISSING>"
    country = "GB"
    loc = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<button class="vs-store-btn">' in line:
            items = line.split('<button class="vs-store-btn">')
            for item in items:
                if '<div class="vs-store-address">' in item:
                    name = item.split("<strong>")[1].split("<")[0]
                    phone = (
                        item.split('<div class="vs-store-address">')[1]
                        .split("<strong>")[1]
                        .split("<")[0]
                    )
                    addinfo = item.split('<div class="vs-store-address">')[1].split(
                        "<br><br> <strong>"
                    )[0]
                    zc = addinfo.rsplit(">", 1)[1].strip()
                    state = "<MISSING>"
                    add = addinfo.rsplit("<br>", 2)[0].strip().replace("<br>", "")
                    city = addinfo.rsplit("<br>", 2)[1].strip()
                    if "Upper Level 3 Birmingham" in add:
                        city = "Birmingham"
                        add = add.split(" Birmingham")[0].strip()
                    if "Glasgow" in add:
                        add = add.split("Glasgow")[0].strip()
                        city = "Glasgow"
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
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
