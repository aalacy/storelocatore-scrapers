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

logger = SgLogSetup().get_logger("dominos_com_py")


def fetch_data():
    url = "https://www.dominos.com.py/contact"
    r = session.get(url, headers=headers)
    website = "dominos.com.py"
    typ = "<MISSING>"
    country = "PY"
    loc = "<MISSING>"
    hours = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    sids = []
    adds = []
    city = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '<option value="' in line:
            sids.append(
                line.split('<option value="')[1].split('"')[0]
                + "|"
                + line.split('">')[1].split("<")[0]
            )
        if "<li>" in line and "+595" not in line:
            adds.append(line.split("<li>")[1].split("<")[0])
    for x in range(0, len(sids)):
        phone = "<MISSING>"
        city = "<MISSING>"
        store = sids[x].split("|")[0]
        name = sids[x].split("|")[1]
        add = adds[x]
        if "Stma. Trinidad" in name:
            city = "Asuncion"
            phone = "+595 21 413 5000"
        if "Sajonia" in name:
            city = "Asuncion"
            phone = "+595 972 575947"
        if "Mora - Norte" in name:
            phone = "0984712412"
        if "11 de Septiembre" in add:
            city = "Fernando de la Mora"
            phone = "+595 41 35000"
        if "Villa Elisa" in name:
            city = "Villa Elisa"
            phone = "+595 984 528865"
        if "Itaugua" in name:
            phone = "0983111222"
            city = "Itaugua"
        if "San Bernardino" in name:
            phone = "595214135000"
            city = "San Bernardino"
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
    name = "Villa Morra"
    city = "Asuncion"
    add = "Quesada"
    phone = "+595 981 376179"
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
    name = "Mundimar"
    city = "Asuncion"
    add = "P96V+RGV"
    phone = "0982662018"
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
    name = "Villa Aurelia"
    city = "Villa Aurelia"
    add = "<MISSING>"
    phone = "0986407419"
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
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
