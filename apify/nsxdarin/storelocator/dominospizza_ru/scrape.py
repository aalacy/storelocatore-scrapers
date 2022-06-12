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
    url = "https://fe.dominospizza.ru/api/address/getCities"
    cities = []
    r = session.get(url, headers=headers)
    for item in json.loads(r.content):
        cities.append(str(item["id"]) + "|" + item["name"] + "|" + item["cityUrl"])
    website = "dominospizza.ru"
    typ = "<MISSING>"
    country = "RU"
    state = "<MISSING>"
    zc = "<MISSING>"
    for cid in cities:
        logger.info(str(cid))
        city = cid.split("|")[1]
        stub = cid.split("|")[2]
        curl = (
            "https://fe.dominospizza.ru/api/store/differentCityStores?cityCode="
            + cid.split("|")[0]
        )
        r2 = session.get(curl, headers=headers)
        loc = stub + ".dominospizza.ru"
        for item in json.loads(r2.content):
            store = item["id"]
            hours = item["availableFrom"] + "-" + item["availableUntil"]
            name = item["name"]
            add = item["address"]
            phone = item["phone"]
            try:
                lng = item["longitude"]
            except:
                lng = "<MISSING>"
            try:
                lat = item["lattitude"]
            except:
                lat = "<MISSING>"
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
