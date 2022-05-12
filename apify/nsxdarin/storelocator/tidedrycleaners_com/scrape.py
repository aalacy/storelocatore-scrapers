from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    weekdays = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    url = "https://consumer.tidelaundry.com/v1/servicepoints?maxLatitude=64.93218366344629&maxLongitude=-63.19580074023439&minLatitude=14.87138826455165&minLongitude=-173.33038325976564&statuses=1&statuses=2&statuses=3"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = line.replace('"address":{"id":', '"address":{"ID').replace(
            '"market":{"id":', '"market":{"ID"'
        )
        if '{"id":' in line:
            items = line.split('{"id":')
            for item in items:
                if ',"name":"' in item:
                    website = "tidedrycleaners.com"
                    country = "US"
                    store = item.split(",")[0]
                    loc = "https://tidecleaners.com/en-us/locations/" + store
                    name = item.split(',"name":"')[1].split('"')[0]
                    lat = item.split('"latitude":')[1].split(",")[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    add = item.split('streetLine1":"')[1].split('"')[0]
                    try:
                        tid = item.split('"typeId":')[1].split(",")[0]
                    except:
                        tid = "<MISSING>"
                    typ = "<MISSING>"
                    try:
                        add = add + " " + item.split('streetLine2":"')[1].split('"')[0]
                    except:
                        pass
                    add = add.strip()
                    try:
                        city = item.split(',"city":"')[1].split('"')[0]
                    except:
                        city = "<MISSING>"
                    state = item.split('"state":"')[1].split('"')[0]
                    try:
                        zc = item.split('"zipCode":"')[1].split('"')[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        phone = item.split('"phoneNumber":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                    if tid == "1":
                        typ = "Store"
                    if tid == "3":
                        typ = "Locker"
                    hours = ""
                    days = (
                        item.split('hoursOfOperation":[')[1]
                        .split("]")[0]
                        .split('{"weekday":')
                    )
                    for day in days:
                        if '"opensLocal":"' in day:
                            daynum = day.split(",")[0]
                            dayname = weekdays[int(daynum)]
                            hrs = (
                                dayname
                                + ": "
                                + day.split('"opensLocal":"')[1].split('"')[0]
                                + "-"
                                + day.split('"closesLocal":"')[1].split('"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    if hours == "":
                        hours = "<MISSING>"
                    if '"locationTypeId":' in item:
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
