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

logger = SgLogSetup().get_logger("lolliandpops_com")


def fetch_data():
    logger.info("Pulling Stores")
    url = "https://storemapper-herokuapp-com.global.ssl.fastly.net/api/users/4652/stores.js?callback=SMcallback2"
    r = session.get(url, headers=headers)
    website = "lolliandpops.com"
    typ = "<MISSING>"
    country = "US"
    loc = "https://www.lolliandpops.com/pages/stores"
    hours = "<MISSING>"
    for line in r.iter_lines():
        if '"id":' in line:
            items = line.split('"id":')
            for item in items:
                if "SMcallback2" not in item:
                    store = item.split(",")[0]
                    name = item.split(',"name":"')[1].split('"')[0]
                    addinfo = item.split('"address":"')[1].split('"')[0]
                    if addinfo.count(",") == 3:
                        add = addinfo.split(",")[0].strip()
                        city = addinfo.split(",")[1].strip()
                        state = addinfo.split(",")[2].strip()
                        zc = addinfo.split(",")[3].strip()
                    else:
                        add = (
                            addinfo.split(",")[0].strip()
                            + " "
                            + addinfo.split(",")[1].strip()
                        )
                        city = addinfo.split(",")[2].strip()
                        state = addinfo.split(",")[3].strip()
                        zc = addinfo.split(",")[4].strip()
                    phone = item.split(',"phone":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
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
