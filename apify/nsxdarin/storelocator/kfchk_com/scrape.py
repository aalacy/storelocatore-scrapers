from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("kfchk_com")


def fetch_data():
    url = "https://corp.kfchk.com/filemanager/system/en/js/restaurant.js"
    r = session.get(url, headers=headers)
    website = "kfchk.com"
    typ = "<MISSING>"
    country = "HK"
    loc = "https://corp.kfchk.com/filemanager/system/en/js/restaurant.js"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    locs = {}
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if ".name='" in line and "//" not in line:
            name = line.split(".name='")[1].split("';")[0]
            rid = line.split(".name")[0].strip().replace("\t", "")
            add = ""
            phone = ""
            hrs = ""
            state = ""
        if ".address='" in line and "//" not in line:
            add = line.split(".address='")[1].split("';")[0]
        if ".openingtime.push('" in line:
            hrs = line.split(".openingtime.push('")[1].split("');")[0]
        if ".tel.push('" in line and "//" not in line:
            phone = line.split(".tel.push('")[1].split("');")[0]
        if ".fax.push(" in line:
            locs[rid] = name + "|" + add + "|" + phone + "|" + hrs
        if (
            ".addChild(" in line
            and "//" not in line
            and "root_restaurant" not in line
            and "hki.addChild" not in line
            and "kowloon.addChild" not in line
            and "nt.addChild" not in line
            and "macau.addChild" not in line
            and "outlying_islands." not in line
        ):
            rid = line.split("(")[1].split(")")[0]
            info = locs[rid]
            name = info.split("|")[0]
            add = info.split("|")[1]
            phone = info.split("|")[2]
            hours = info.split("|")[3]
            zc = "<MISSING>"
            city = "<MISSING>"
            state = "<MISSING>"
            name = name.replace("\\'", "'")
            add = add.replace("\\'", "'")
            if "Hong Kong" in add:
                city = "Hong Kong"
                add = add.replace("Hong Kong", "").strip()
            if "Kowloon" in add:
                city = "Kowloon"
                add = add.replace("Kowloon", "").strip()
            if "Macau" in add:
                city = "Macau"
                add = add.replace("Macau", "").strip()
                country = "MO"
            if hours == "":
                hours = "<MISSING>"
            if "0" not in hours:
                hours = "<MISSING>"
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
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
