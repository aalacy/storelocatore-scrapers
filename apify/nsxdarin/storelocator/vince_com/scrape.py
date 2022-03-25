from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("vince_com")


def fetch_data():
    url = "https://www.vince.com/on/demandware.store/Sites-vince-Site/default/Stores-GetNearestStores?latitude=40.7135097&longitude=-73.9859414&countryCode=&distanceUnit=mi&maxdistance=100000"
    r = session.get(url, headers=headers)
    website = "vince.com"
    typ = "<MISSING>"
    loc = "<MISSING>"
    store = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '"name":"' in line:
            items = line.split('"name":"')
            for item in items:
                CS = False
                if '"storeSecondaryName":"' in item:
                    if "Coming Soon" in item:
                        CS = True
                    loc = "<MISSING>"
                    hours = ""
                    store = "<MISSING>"
                    name = item.split('"')[0]
                    country = item.split('"countryCode":"')[1].split('"')[0]
                    add = item.split('"address1":"')[1].split('"')[0]
                    add = add + " " + item.split('"address2":"')[1].split('"')[0]
                    add = add.strip()
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    city = item.split('"city":"')[1].split('"')[0]
                    state = item.split('"stateCode":"')[1].split('"')[0]
                    phone = item.split('"phone":"')[1].split('"')[0]
                    raw_address = add + " " + city + ", " + state + " " + zc
                    raw_address = raw_address.strip()
                    lat = item.split('"latitude":"')[1].split('"')[0]
                    lng = item.split('"longitude":"')[1].split('"')[0]
                    try:
                        hrs = item.split(',"storeHours":"')[1].split(
                            '","storeEvents":'
                        )[0]
                        cleanr = re.compile("<.*?>")
                        hours = re.sub(cleanr, "", hrs)
                    except:
                        hours = "<MISSING>"
                    hours = hours.replace("&:amp;", "&")
                    if "Temporarily" in item:
                        hours = "Temporarily Closed"
                    typ = item.split('"storeTypeDisplay":"')[1].split('"')[0]
                    if phone == "":
                        phone = "<MISSING>"
                    if zc == "":
                        zc = "<MISSING>"
                    if "0" not in hours:
                        hours = "<MISSING>"
                    hours = hours.replace("pm", "pm;").replace(";;", ";").strip()
                    if "Same day" in hours:
                        hours = hours.split("Same day")[0].strip()
                    add = add.replace("International Market Place", "").strip()
                    if "El Paseo Village" in add:
                        add = add.split("Paseo Village")[1].strip()
                    if "587 Newport" in add:
                        hours = "Sun: 12:00pm-6:00pm; Mon-Sat: 11:00am-7:00pm"
                    if "; Friday 12/24" in hours:
                        hours = hours.split("; Friday 12/24")[0]
                    add = add.replace("RUSSIA", "").strip()
                    if "(" in add:
                        add = add.rsplit("(", 1)[0].strip()
                    if "(" in city:
                        city = city.split("(")[0].strip()
                    if "," in city:
                        city = city.split(",")[1].strip()
                    if country == "IT" and " " in city:
                        if len(city.rsplit(" ", 1)[1]) == 2:
                            city = city.rsplit(" ", 1)[0].strip()
                    if "Stockholm" in city:
                        city = "Stockholm"
                    if "103" in city:
                        city = city.split("103")[0].strip()
                    if "Draycott Avenue" not in add:
                        if CS is False:
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
                                raw_address=raw_address,
                                hours_of_operation=hours,
                            )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
