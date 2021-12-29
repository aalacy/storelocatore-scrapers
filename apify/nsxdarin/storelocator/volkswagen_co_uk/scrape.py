from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import json
import time

logger = SgLogSetup().get_logger("volkswagen_co_uk")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    letters = [
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "m",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "u",
        "v",
        "w",
        "x",
        "y",
        "z",
    ]
    pids = []
    for letter in letters:
        logger.info(letter)
        url = (
            "https://prod-ds.vwa-d.cc/v1-91-0/bff-search/suggestions?serviceConfigsServiceConfig=%7B%22key%22%3A%22service-config%22%2C%22urlOrigin%22%3A%22https%3A%2F%2Fwww.volkswagen.co.uk%22%2C%22urlPath%22%3A%22%2Fen.service-config.json%22%2C%22tenantCommercial%22%3Anull%2C%22tenantPrivate%22%3Anull%2C%22customConfig%22%3Anull%2C%22homePath%22%3Anull%2C%22credentials%22%3A%7B%22username%22%3A%22%22%2C%22password%22%3A%22%22%7D%7D&query=%7B%22type%22%3A%22SUGGESTION%22%2C%22name%22%3A%22"
            + letter.upper()
            + "%22%2C%22countryCode%22%3A%22GB%22%2C%22language%22%3A%22en%22%2C%22dealerServiceFilter%22%3A%5B%5D%2C%22userServiceFilter%22%3A%5B%5D%2C%22contentDealerServiceFilter%22%3A%5B%5D%7D"
        )
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '{"type":"LOCATION"' in line:
                items = line.split('{"type":"LOCATION"')
                for item in items:
                    if ',"placeId":"' in item:
                        pid = item.split(',"placeId":"')[1].split('"')[0]
                        if pid not in pids:
                            pids.append(pid)
    for pid in pids:
        url = (
            "https://prod-ds.vwa-d.cc/v1-91-0/bff-search/search_searchDealersByLocation?serviceConfigsServiceConfig=%7B%22key%22%3A%22service-config%22%2C%22urlOrigin%22%3A%22https%3A%2F%2Fwww.volkswagen.co.uk%22%2C%22urlPath%22%3A%22%2Fen.service-config.json%22%2C%22tenantCommercial%22%3Anull%2C%22tenantPrivate%22%3Anull%2C%22customConfig%22%3Anull%2C%22homePath%22%3Anull%2C%22credentials%22%3A%7B%22username%22%3A%22%22%2C%22password%22%3A%22%22%7D%7D&query=%7B%22type%22%3A%22PLACE%22%2C%22placeId%22%3A%22"
            + pid
            + "%22%2C%22language%22%3A%22en%22%2C%22countryCode%22%3A%22GB%22%2C%22dealerServiceFilter%22%3A%5B%5D%2C%22userServiceFilter%22%3A%5B%5D%2C%22contentDealerServiceFilter%22%3A%5B%5D%7D"
        )
        logger.info(pid)
        r2 = session.get(url, headers=headers)
        website = "volkswagen.co.uk"
        typ = "<MISSING>"
        country = "GB"
        for item in json.loads(r2.content)["dealers"]:
            lurl = item["contact"]["website"]
            name = item["name"]
            store = item["id"]
            city = item["address"]["city"]
            state = "<MISSING>"
            phone = item["contact"]["phoneNumber"]
            zc = item["address"]["postalCode"]
            add = item["address"]["street"]
            lat = item["coordinates"][0]
            lng = item["coordinates"][1]
            hours = ""
            OHFound = False
            try:
                r3 = session.get(lurl, headers=headers)
                time.sleep(5)
                for line3 in r3.iter_lines():
                    if '"openingHours": [' in line3 and hours == "":
                        OHFound = True
                    if OHFound and "]," in line3:
                        OHFound = False
                    if OHFound and "-" in line3:
                        hrs = line3.split('"')[1]
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            except:
                pass
            if hours == "":
                hours = "<MISSING>"
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
