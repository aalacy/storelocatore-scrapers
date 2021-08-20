from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("mybpstation_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    ids = []
    boxes = ["18.91619|-171.791110603|71.3577635769|-66.96466"]
    while len(boxes) >= 1:
        swlat = boxes[0].split("|")[0]
        swlng = boxes[0].split("|")[1]
        nelat = boxes[0].split("|")[2]
        nelng = boxes[0].split("|")[3]
        boxes.pop(0)
        url = (
            "https://bpretaillocator.geoapp.me/api/v1/locations/within_bounds?sw%5B%5D="
            + swlat
            + "&sw%5B%5D="
            + swlng
            + "&ne%5B%5D="
            + nelat
            + "&ne%5B%5D="
            + nelng
            + "&key=AIzaSyDHlZ-hOBSpgyk53kaLADU18wq00TLWyEc&format=json"
        )
        r = session.get(url, headers=headers)
        for item in json.loads(r.content):
            try:
                sw1 = (
                    str(item["bounds"]["sw"])
                    .split(",")[0]
                    .replace("[", "")
                    .replace(" ", "")
                    .replace("]", "")
                )
                sw2 = (
                    str(item["bounds"]["sw"])
                    .split(",")[1]
                    .replace("[", "")
                    .replace(" ", "")
                    .replace("]", "")
                )
                ne1 = (
                    str(item["bounds"]["ne"])
                    .split(",")[0]
                    .replace("[", "")
                    .replace(" ", "")
                    .replace("]", "")
                )
                ne2 = (
                    str(item["bounds"]["ne"])
                    .split(",")[1]
                    .replace("[", "")
                    .replace(" ", "")
                    .replace("]", "")
                )
                newbox = sw1 + "|" + sw2 + "|" + ne1 + "|" + ne2
                boxes.append(newbox)
            except:
                pass
        logger.info("Areas Remaining: " + str(len(boxes)))
        for line in r.iter_lines():
            line = str(line.decode("utf-8"))
            if '{"id":"' in line:
                items = line.split('{"id":"')
                for item in items:
                    if '"name":"' in item:
                        name = item.split('"name":"')[1].split('"')[0]
                        lat = item.split('"lat":')[1].split(",")[0]
                        lng = item.split('"lng":')[1].split(",")[0]
                        add = item.split('"address":"')[1].split('"')[0]
                        city = item.split('"city":"')[1].split('"')[0]
                        state = item.split('"state":"')[1].split('"')[0]
                        zc = item.split('"postcode":"')[1].split('"')[0]
                        country = item.split('"country_code":"')[1].split('"')[0]
                        phone = item.split('"telephone":"')[1].split('"')[0]
                        try:
                            typ = item.split('"site_brand":"')[1].split('"')[0]
                        except:
                            typ = "<MISSING>"
                        website = "mybpstation.com"
                        loc = "https://www.bp.com/en_us/united-states/home/find-a-gas-station.html"
                        store = item.split('"')[0]
                        storeinfo = name + "|" + add + "|" + city + "|" + lat
                        hours = ""
                        if '"opening_hours":[]' in item:
                            hours = "<MISSING>"
                        else:
                            days = (
                                item.split('"opening_hours":[')[1]
                                .split(',"open_status":"')[0]
                                .split('"days":["')
                            )
                            for day in days:
                                if '"hours":[["' in day:
                                    hrs = (
                                        day.split("]")[0]
                                        .replace('"', "")
                                        .replace(",", "-")
                                        + ": "
                                        + day.split('"hours":[["')[1]
                                        .split("]")[0]
                                        .replace('"', "")
                                        .replace(",", "-")
                                    )
                                    if hours == "":
                                        hours = hrs
                                    else:
                                        hours = hours + "; " + hrs
                        if phone == "":
                            phone = "<MISSING>"
                        if storeinfo not in ids and country == "US":
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
                            ids.append(storeinfo)


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
