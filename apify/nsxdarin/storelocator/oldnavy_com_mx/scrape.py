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

logger = SgLogSetup().get_logger("oldnavy_com_mx")


def fetch_data():
    url = "https://oldnavy.gap.com/Asset_Archive/ONWeb/content/pages/mexico/tiendas/tiendas.html?mlink=0,0,mx_nav&clink=0&v=1&cb=544"
    r = session.get(url, headers=headers)
    website = "oldnavy.com.mx"
    typ = "<MISSING>"
    country = "MX"
    loc = "<MISSING>"
    store = "<MISSING>"
    adds = []
    coords = []
    hoursarray = []
    names = []
    phones = []
    CFound = False
    HFound = False
    AFound = False
    PFound = False
    NFound = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if "STORE_DIRECTIONS:" in line:
            CFound = True
        if CFound and "]," in line:
            CFound = False
        if CFound and "www.google.com/maps/" in line:
            if "!2d" in line:
                clng = line.split("!2d")[1].split("!")[0]
                clat = line.split("!3d")[1].split("!")[0]
                coords.append(clat + "|" + clng)
            if "@" in line:
                clat = line.split("@")[1].split(",")[0]
                clng = line.split("@")[1].split(",")[1]
                coords.append(clat + "|" + clng)
        if "STORE_ADDRESSES:" in line:
            AFound = True
        if AFound and "]," in line:
            AFound = False
        if AFound and "<br/>" in line:
            add = line.split("<br/>")[1]
            city = line.split("<br/>")[2]
            state = line.split("<br/>")[3].rsplit(" ", 1)[0]
            zc = line.split("<br/>")[3].rsplit(" ", 1)[1]
            adds.append(add + "|" + city + "|" + state + "|" + zc)
        if "STORE_HOURS:" in line:
            HFound = True
        if HFound and "]," in line:
            HFound = False
        if HFound and "[" not in line:
            if "', '" in line:
                items = line.split("', '")
                for item in items:
                    if "m" in item:
                        hoursarray.append(
                            item.replace("\r", "")
                            .replace("\t", "")
                            .replace("\n", "")
                            .replace("'", "")
                            .strip()
                        )
            else:
                hoursarray.append(
                    line.replace("\t", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .strip()
                    .replace("'", "")
                )
        if "STORE_PHONES: [" in line:
            PFound = True
        if PFound and "]," in line:
            PFound = False
        if PFound and "[" not in line:
            items = line.split("', '")
            for item in items:
                if "(" in item:
                    phones.append(
                        item.replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("'", "")
                        .strip()
                    )
        if "STORE_NAMES:" in line:
            NFound = True
        if NFound and "]," in line:
            NFound = False
        if NFound and "[" not in line:
            items = line.split("', '")
            for item in items:
                if (
                    "a" in item
                    or "e" in item
                    or "u" in item
                    or "o" in item
                    or "i" in item
                ):
                    names.append(
                        item.replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                        .replace("'", "")
                        .strip()
                    )
    for x in range(0, len(names)):
        name = names[x]
        add = adds[x].split("|")[0]
        city = adds[x].split("|")[1]
        state = adds[x].split("|")[2]
        zc = adds[x].split("|")[3]
        lat = coords[x].split("|")[0]
        lng = coords[x].split("|")[1]
        typ = "Old Navy"
        name = "Old Navy"
        hours = hoursarray[x]
        phone = phones[x]
        hours = hours.replace("Abierto de ", "")
        phone = phone.replace(",", "")
        hours = hours.replace(",", "")
        if "Parque Tezontle" in name:
            lat = "-99.0838208486921"
        if "cerrada" not in hours:
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
    name = "Old Navy"
    typ = "Old Navy"
    lat = "19.384574"
    lng = "-99.082539"
    add = "Avenida Canal de Tezontle #1512 Col. Alfonso Ortiz Tirado"
    state = "Ciudad de Mexico C.P."
    city = "Delegación Iztapalapa"
    zc = "9020"
    hours = "Abierto de lunes a domingo de 11:00 a.m. a 9:00 p.m."
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
