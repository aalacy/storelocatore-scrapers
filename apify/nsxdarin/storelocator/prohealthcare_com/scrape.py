from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "CSRF-Token": "undefined",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.prohealthcare.com/content/prohealth/en/provider-lookup/serp.html?isAcceptingNewPatients=true&search=10002&latitude=40.7135097&longitude=-73.9859414&network=ProHEALTHCare",
}

logger = SgLogSetup().get_logger("prohealthcare_com")


def fetch_data():
    infos = []
    for clat in range(35, 45):
        for clng in range(-70, -80, -1):
            logger.info(str(clat) + "," + str(clng))
            url = "https://www.prohealthcare.com/bin/optumcare/findlocations"
            payload = {
                "latitude": str(clat),
                "longitude": str(clng),
                "search": "",
                "network": "ProHEALTHCare",
                "radius": "100mi",
            }
            r = session.post(url, headers=headers, data=json.dumps(payload))
            website = "prohealthcare.com"
            typ = "<MISSING>"
            country = "US"
            loc = "https://www.prohealthcare.com/bin/optumcare/findlocations"
            store = "<MISSING>"
            hours = "<MISSING>"
            for line in r.iter_lines():
                if '"individualProviderId":"' in line:
                    items = line.split('"individualProviderId":"')
                    for item in items:
                        if "providerRole" in item:
                            hours = ""
                            zc = item.split('"zip":"')[1].split('"')[0]
                            typ = item.split('{"specialty":"')[1].split('"')[0]
                            city = item.split('"city":"')[1].split('"')[0]
                            state = item.split('"state":"')[1].split('"')[0]
                            lat = (
                                item.split('"lat_lon":"')[1].split('"')[0].split(",")[0]
                            )
                            lng = (
                                item.split('"lat_lon":"')[1].split('"')[0].split(",")[1]
                            )
                            add = item.split('"line1":"')[1].split('"')[0]
                            name = item.split('"businessName":"')[1].split('"')[0]
                            try:
                                phone = item.split('","telephoneUsage":"Office Phone"')[
                                    0
                                ].rsplit('telephoneNumber":"', 1)[1]
                                phone = phone.replace("+1 ", "")
                            except:
                                phone = "<MISSING>"
                            days = item.split('"dayOfWeek":"')
                            for day in days:
                                if '"fromHour":"' in day:
                                    hrs = (
                                        day.split('One"')[0]
                                        + ": "
                                        + day.split('"fromHour":"')[1].split('"')[0]
                                        + "-"
                                        + day.split('"toHour":"')[1].split('"')[0]
                                    )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                            if hours == "":
                                hours = "<MISSING>"
                            addinfo = (
                                add
                                + "|"
                                + city
                                + "|"
                                + name
                                + "|"
                                + state
                                + "|"
                                + lat
                                + "|"
                                + phone
                            )
                            if addinfo not in infos:
                                infos.append(addinfo)
                                if "100-33 4th Ave" in add:
                                    phone = "347-909-7044"
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
