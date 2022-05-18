from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json

logger = SgLogSetup().get_logger("greyhound_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json;charset=UTF-8",
    "authority": "openair-california.airtrfx.com",
    "accept": "application/json, text/plain, */*",
    "origin": "https://www.greyhound.com",
    "referer": "https://www.greyhound.com/en-us/destinations",
    "em-api-key": "HeQpRjsFI5xlAaSx2onkjc1HTK0ukqA1IrVvd5fvaMhNtzLTxInTpeYB1MK93pah",
}


def fetch_data():
    url = "https://openair-california.airtrfx.com/hangar-service/v2/ghl/airports/search"
    payload = {
        "outputFields": ["name", "extraInfo", "city", "state", "iataCode"],
        "geoField": {"value": 50000, "name": "geo", "geoFromGeoId": "-556600004"},
        "sortingDetails": [{"field": "geo", "order": "ASC"}],
        "filterFields": [{"name": "active", "values": ["true"]}],
        "setting": {"airportSource": "TRFX", "routeSource": "TRFX"},
        "from": 0,
        "size": 1000,
        "language": "en",
    }
    r = session.post(url, headers=headers, data=json.dumps(payload))
    for line in r.iter_lines():
        if '{"name":"' in line:
            items = line.split('{"name":"')
            for item in items:
                if "iataCode" in item:
                    name = item.split('"')[0]
                    store = item.split('iataCode":"')[1].split('"')[0]
                    city = item.split(',"name":"')[1].split('"')[0]
                    state = item.split('"identifierCode":"')[1].split('"')[0]
                    lng = item.split('"longitude":')[1].split(",")[0]
                    lat = item.split('"latitude":')[1].split("}")[0]
                    hrs = item.split('"hoursBusStation":')[1].split(']},"')[0]
                    phone = item.split('"phoneNumberMain":"')[1].split('"')[0]
                    typ = item.split('"stationStopType":"')[1].split('"')[0]
                    zc = item.split('"postalCode":"')[1].split('"')[0]
                    add = item.split('"street":"')[1].split('"')[0]
                    website = "greyhound.ca"
                    lurl = "<MISSING>"
                    country = "CA"
                    try:
                        hours = (
                            "Sun: "
                            + hrs.split('"1":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"1":')[1].split('"close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Mon: "
                            + hrs.split('"2":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"2":')[1].split('"close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Tue: "
                            + hrs.split('"3":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"3":')[1].split('"close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Wed: "
                            + hrs.split('"4":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"4":')[1].split('"close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Thu: "
                            + hrs.split('"5":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"5":')[1].split('"close":"')[1].split('"')[0]
                        )
                        hours = (
                            hours
                            + "; Fri: "
                            + hrs.split('"6":')[1].split('"open":"')[1].split('"')[0]
                            + "-"
                            + hrs.split('"6":')[1].split('"close":"')[1].split('"')[0]
                        )
                    except:
                        hours = "<MISSING>"
                    cname = item.split('"countryName":"')[1].split('"')[0]
                    if cname == "Canada":
                        yield SgRecord(
                            locator_domain=website,
                            page_url=lurl,
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
