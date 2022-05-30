# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("carlsjr_ru")


def fetch_data():
    urls = [
        "http://carlsjr-russia.ru/contacts-piter",
        "http://carlsjr-russia.ru/contacts-moscow",
        "http://carlsjr-russia.ru/contacts-novosib",
        "http://carlsjr-russia.ru/contacts-norilsk",
        "http://carlsjr-russia.ru/contacts-chita",
    ]
    for url in urls:
        logger.info(url)
        coords = []
        r = session.get(url, headers=headers)
        website = "carlsjr.ru"
        loc = url
        typ = "<MISSING>"
        country = "RU"
        phone = "<MISSING>"
        lines = r.iter_lines()
        locinfo = []
        for line in lines:
            if '"coordinates": [' in line or 'coordinates":[' in line:
                clat = line.split("[")[1].split(",")[0]
                clng = line.split("[")[1].split(",")[1].split("]")[0].strip()
                coords.append(clat + "|" + clng)
            if 'field="li_descr__' in line:
                name = (
                    line.split('field="li_title__')[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
                add = (
                    line.split('field="li_descr__')[1]
                    .split(">")[1]
                    .split("<")[0]
                    .strip()
                )
                try:
                    city = line.split("Метро:")[1].split("<")[0].strip()
                except:
                    try:
                        city = line.split("м.")[1].split("<")[0].strip()
                    except:
                        city = "<MISSING>"
                try:
                    state = line.split("Район:")[1].split("<")[0].strip()
                except:
                    state = "<MISSING>"
                if "<br />П" in line:
                    hours = "П" + line.split("<br />П")[1].split("</div>")[0].replace(
                        "<br /><br />", "; "
                    ).replace("<br />", ": ")
                else:
                    hours = "<MISSING>"
                locinfo.append(
                    name + "|" + add + "|" + city + "|" + state + "|" + hours
                )
            if "</html>" in line:
                for x in range(0, len(coords)):
                    store = "<MISSING>"
                    name = locinfo[x].split("|")[0]
                    add = locinfo[x].split("|")[1]
                    city = locinfo[x].split("|")[2]
                    state = locinfo[x].split("|")[3]
                    hours = locinfo[x].split("|")[4]
                    lat = coords[x].split("|")[0]
                    lng = coords[x].split("|")[1]
                    zc = "<MISSING>"
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
