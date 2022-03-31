# -*- coding: cp1252 -*-
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
    url = "https://www.google.com/maps/d/u/0/embed?mid=16YXX8H26VmikOUKpJM6dpZUKkYd9FDIc&ll=-25.324991015573804%2C-57.49491050000001&z=11"
    r = session.get(url, headers=headers)
    website = "dominos.com.py"
    typ = "<MISSING>"
    country = "PY"
    store = "<MISSING>"
    loc = "<MISSING>"
    hours = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    names = []
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '[\\"Nombre\\",[\\"' in line:
            items = line.split('[\\"Nombre\\",[\\"')
            for item in items:
                if (
                    "numero para delivery " in item
                    and "_pageData" not in item
                    and ",null,[],[]],null" not in item
                ):
                    name = item.split('\\"]')[0].replace("\\u0027", "'")
                    add = ""
                    try:
                        phone = item.split("para delivery ")[1].split("\\")[0]
                    except:
                        phone = "<MISSING>"
                    lat = "-" + item.split("[-")[1].split(",")[0]
                    lng = item.split("[-")[1].split(",")[1].split("]")[0]
                    if "Stma. Trinidad" in name:
                        city = "Asuncion"
                        phone = "+595 21 413 5000"
                        add = "Stma. Trinidad Stma. Trinidad. Avda. Stma. Trinidad esq. Sacramento."
                    if "Sajonia" in name:
                        city = "Asuncion"
                        phone = "+595 972 575947"
                        add = "Sajonia Avda. Carlos A. López esq. Dr. Emilio Paiva."
                    if "Mora - Norte" in name:
                        phone = "0984712412"
                    if "de la Mora" in name:
                        add = "Fdo. de la Mora 11 de Septiembre y Músicos del Chaco."
                        city = "Fernando de la Mora"
                        phone = "+595 41 35000"
                    if "Villa Elisa" in name:
                        add = "Villa Elisa Avda. Von Polesky"
                        city = "Villa Elisa"
                        phone = "+595 984 528865"
                    if "Itaugua" in name:
                        add = "Itaugua Victoriano Aldama, Itauguá"
                        phone = "0983111222"
                        city = "Itaugua"
                    if "San Bernardino" in name:
                        add = "San Bernardino San Bernadino"
                        phone = "595214135000"
                        city = "San Bernardino"
                    if "Villa Morra" in name:
                        city = "Asuncion"
                        add = "Quesada"
                    if "Mundimar" in name:
                        city = "Asuncion"
                        add = "P96V+RGV"
                    if "Villa Aurelia" in name:
                        city = "Villa Aurelia"
                        add = "<MISSING>"
                    if (
                        name != "Domino's Pizza Villa Morra"
                        and name != "Domino's Pizza Villa Aurelia"
                        and name != "Domino's Pizza Sajonia"
                        and name != "Domino's Pizza Fernando Norte"
                        and name not in names
                    ):
                        names.append(name)
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
