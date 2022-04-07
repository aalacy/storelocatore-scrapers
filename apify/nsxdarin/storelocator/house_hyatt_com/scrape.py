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

logger = SgLogSetup().get_logger("house_hyatt_com")


def fetch_data():
    url = "https://www.hyatt.com/explore-hotels/service/hotels"
    r = session.get(url, headers=headers)
    website = "house.hyatt.com"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"spiritCode":"' in line:
            items = line.split('"spiritCode":"')
            for item in items:
                if '"brand":{"key":"' in item:
                    phone = "<MISSING>"
                    CS = False
                    name = item.split('"name":"')[1].split('"')[0]
                    loc = (
                        "https://www.hyatt.com"
                        + item.split('"url":"https://www.hyatt.com')[1].split('"')[0]
                    )
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split("}")[0]
                    hours = "<MISSING>"
                    typ = (
                        item.split('"brand":{"key":"')[1]
                        .split('"label":"')[1]
                        .split('"')[0]
                    )
                    store = item.split('"')[0]
                    country = item.split('"country":{"key":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    zc = item.split('"zipcode":"')[1].split('"')[0]
                    add = item.split('"addressLine1":"')[1].split('"')[0]
                    try:
                        add = (
                            add + " " + item.split('"addressLine2":"')[1].split('"')[0]
                        )
                    except:
                        pass
                    try:
                        state = item.split('"stateProvince":{"key":"')[1].split('"')[0]
                    except:
                        state = "<MISSING>"
                    zc = item.split('"zipcode":"')[1].split('"')[0]
                    if loc == "":
                        loc = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    if typ == "":
                        typ = "<MISSING>"
                    logger.info(loc)
                    try:
                        r2 = session.get(loc, headers=headers)
                        for line2 in r2.iter_lines():
                            line2 = str(line2.decode("utf-8"))
                            if ">Coming " in line2:
                                CS = True
                            if ">Opening " in line2:
                                CS = True
                            if '"telephone":"' in line2:
                                phone = line2.split('"telephone":"')[1].split('"')[0]
                    except:
                        pass
                    if "wasxs" in loc:
                        CS = False
                    if "Club Maui, " in name:
                        name = "Hyatt Residence Club Maui, Kaanapali Beach"
                    if CS:
                        hours = "Coming Soon"
                    if "dxbzm" in loc:
                        hours = "<MISSING>"
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
