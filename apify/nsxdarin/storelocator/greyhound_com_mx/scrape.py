from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("greyhound_com_mx")


def fetch_data():
    url = "https://www.greyhound.com/en-us/destinations"
    cities = []
    pids = []
    r = session.get(url, headers=headers)
    MFound = False
    for line in r.iter_lines():
        if ">Mexico</span>" in line:
            MFound = True
        if MFound and "United States</span>" in line:
            MFound = False
        if MFound and '<a  href="bus-stations' in line:
            curl = (
                "https://www.greyhound.com/en-us/"
                + line.split('href="')[1].split('"')[0]
            )
            cities.append(curl)
    website = "greyhound.com.mx"
    typ = "<MISSING>"
    country = "MX"
    loc = "<MISSING>"
    hours = "<MISSING>"
    logger.info("Pulling Stores")
    for curl in cities:
        r = session.get(curl, headers=headers)
        logger.info(curl)
        for line in r.iter_lines():
            if 'href="https://www.greyhound.com/redirect?orig=' in line:
                items = line.split('href="https://www.greyhound.com/redirect?orig=')
                for item in items:
                    if 'class="station-item-address' in item:
                        pid = item.split("&")[0]
                        if pid not in pids:
                            pids.append(pid)
    for pid in pids:
        url = "https://openair-california.airtrfx.com/hangar-service/v2/ghl/airports/search"
        payload = {
            "outputFields": ["name", "extraInfo", "city", "state", "iataCode"],
            "sortingDetails": [{"field": "cityName", "order": "ASC"}],
            "filterFields": [
                {"name": "active", "values": ["true"]},
                {"name": "iataCode", "values": [pid]},
            ],
            "setting": {"airportSource": "TRFX", "routeSource": "TRFX"},
            "from": 0,
            "size": 10,
            "language": "en",
        }
        headers2 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
            "content-type": "application/json;charset=UTF-8",
            "em-api-key": "HeQpRjsFI5xlAaSx2onkjc1HTK0ukqA1IrVvd5fvaMhNtzLTxInTpeYB1MK93pah",
            "authority": "openair-california.airtrfx.com",
            "accept": "application/json, text/plain, */*",
            "referer": "https://www.greyhound.com/en-us/bus-station-910272?redirecturl=true",
            "origin": "https://www.greyhound.com",
        }
        r = session.post(url, headers=headers2, data=json.dumps(payload))
        logger.info(pid)
        for line in r.iter_lines():
            if '"name":"' in line:
                store = line.split('"iataCode":"')[1].split('"')[0]
                loc = "https://www.greyhound.com/en-us/bus-station-" + store
                name = line.split('"name":"')[1].split('"')[0]
                city = line.split('"city":')[1].split('"name":"')[1].split('"')[0]
                lat = line.split('"latitude":"')[1].split('"')[0]
                lng = line.split('"longitude":"')[1].split('"')[0]
                state = line.split(',"state":')[1].split('"name":"')[1].split('"')[0]
                try:
                    phone = line.split(',"phoneNumber":"')[1].split('"')[0]
                except:
                    phone = "<MISSING>"
                if phone == "<MISSING>":
                    try:
                        phone = line.split('"phoneNumberMain":"')[1].split('"')[0]
                    except:
                        phone = "<MISSING>"
                typ = line.split('"stationStopType":"')[1].split('"')[0]
                hours = "<MISSING>"
                zc = line.split('"postalCode":"')[1].split('"')[0]
                add = line.split('"street":"')[1].split('"')[0]
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
