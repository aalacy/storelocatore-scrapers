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

logger = SgLogSetup().get_logger("cashmaxtexas_com")


def fetch_data():
    url = "https://www.cashmaxtexas.com/locations.html"
    r = session.get(url, headers=headers)
    website = "cashmaxtexas.com"
    typ = "<MISSING>"
    country = "US"
    allinfo = ""
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        allinfo = allinfo + line.replace("\r", "").replace("\n", "").replace("\t", "")
    items = allinfo.split('"@type":"LocalBusiness","name":"CashMax Title & Loan"')
    for item in items:
        if (
            '"@id":"https://www.cashmaxtexas.com/' in item
            and "#organization" not in item
        ):
            loc = item.split('"url":"')[1].split('"')[0]
            hours = ""
            phone = item.split('"telephone":"+1-')[1].split('"')[0]
            add = item.split('streetAddress":"')[1].split('"')[0]
            zc = item.split('postalCode":"')[1].split('"')[0]
            state = item.split('addressRegion":"')[1].split('"')[0]
            city = item.split('addressLocality":"')[1].split('"')[0]
            name = "Cash Max " + city
            lat = "<MISSING>"
            lng = "<MISSING>"
            store = "<MISSING>"
            days = item.split('"dayOfWeek":["')
            for day in days:
                if ',"opens":"' in day:
                    hrs = (
                        day.split('"]')[0].replace('","', "-")
                        + ": "
                        + day.split(',"opens":"')[1].split('"')[0]
                        + "-"
                        + day.split('"closes":"')[1].split('"')[0]
                    )
                    hrs = hrs.replace("00:00-00:00", "Closed")
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            logger.info(loc)
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                line2 = str(line2.decode("utf-8"))
                if "Address</h3><div>" in line2:
                    add = line2.split("Address</h3><div>")[1].split("<")[0].strip()
            if "austin-tx" not in loc:
                add = add.replace("Old Orchard Village East,", "").strip()
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
