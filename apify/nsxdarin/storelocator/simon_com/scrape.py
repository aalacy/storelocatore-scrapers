from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    website = "simon.com"
    url = "https://api.simon.com/v1.2/centers/all/index"
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        store = item["mallId"]
        typ = item["propertyType"]
        add = item["address"]["street1"] + " " + item["address"]["street2"]
        add = add.strip()
        city = item["address"]["city"]
        state = item["address"]["state"]
        zc = item["address"]["zipCode"]
        country = item["address"]["country"]
        name = item["mallName"]
        phone = item["mallPhone"]
        loc = item["targetUrl"]
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        if loc == "":
            loc = "https://www.simon.com/mall/" + item["urlFriendlyName"]
            r2 = session.get(loc, headers=headers)
            time.sleep(3)
            for line2 in r2.iter_lines():
                if '"Longitude":' in line2:
                    lng = line2.split('"Longitude":')[1].split(",")[0]
                    lat = line2.split('"Latitude":')[1].split(",")[0]
                if '"HoursOutlook":{"' in line2:
                    days = line2.split('StartDaysOfWeekAbbreviation":"')
                    for day in days:
                        if '"HoursOutlook"' not in day:
                            hrs = (
                                day.split('"')[0]
                                + "-"
                                + day.split('EndDaysOfWeekAbbreviation":"')[1].split(
                                    '"'
                                )[0]
                                + ": "
                            )
                            hrs = (
                                hrs
                                + day.split('"OpenTimeDescription":"')[1].split('"')[0]
                                + "-"
                                + day.split('"CloseTimeDescription":"')[1].split('"')[0]
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
                    hours = hours.replace("Sun-Sun", "Sun")
                    hours = hours.replace("Sat-Sat", "Sat")
                    hours = hours.replace("Fri-Fri", "Fri")
                    if hours.count(";") == 3:
                        hours = hours.rsplit(";", 1)[0].strip()
        if hours == "":
            hours = "<MISSING>"
        if loc == "":
            loc = "<MISSING>"
        if "outlet/puerto-rico" in loc:
            lat = "18.438676"
            lng = "-66.540878"
            hours = "Monday - Thursday: 9:00AM - 8:00PM; Friday - Saturday: 9:00AM - 9:00PM; Sunday: 11:00AM - 6:00PM"
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
