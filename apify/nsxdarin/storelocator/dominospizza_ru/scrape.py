# -*- coding: utf-8 -*-
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

logger = SgLogSetup().get_logger("dominospizza_ru")


def fetch_data():
    url = "https://dominospizza.ru/find_dominos?st=del"
    cities = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'cities":[{' in line:
            items = line.split('cities":[{')[1].split('e,"id":')
            for item in items:
                if 'cityUrl":"' in item:
                    cities.append(
                        item.split(",")[0]
                        + "|"
                        + item.split('"name":"')[1].split('"')[0]
                    )
    website = "dominospizza.ru"
    loc = "<MISSING>"
    typ = "<MISSING>"
    country = "RU"
    state = "<MISSING>"
    zc = "<MISSING>"
    for cid in cities:
        logger.info(str(cid))
        city = cid.split("|")[1]
        curl = (
            "https://fe.dominospizza.ru/api/store/differentCityStores?cityCode="
            + cid.split("|")[0]
        )
        r2 = session.get(curl, headers=headers)
        for item in json.loads(r2.content):
            store = item["id"]
            hours = item["availableFrom"] + "-" + item["availableUntil"]
            name = item["name"]
            add = item["address"]
            phone = item["phone"]
            lng = item["longitude"]
            lat = item["lattitude"]
            if "г. " in add:
                try:
                    add = add.split(",", 1)[1].strip()
                except:
                    pass
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
