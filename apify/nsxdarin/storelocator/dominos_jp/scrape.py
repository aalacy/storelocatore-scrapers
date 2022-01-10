# -*- coding: utf-8 -*-
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("dominos_jp")


def fetch_data():
    locs = []
    url = "https://www.dominos.jp/sitemap.aspx"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.dominos.jp/en/store/" in line:
            items = line.split("<loc>https://www.dominos.jp/en/store/")
            for item in items:
                if "<html" not in item:
                    lurl = "https://www.dominos.jp/en/store/" + item.split("<")[0]
                    if lurl != "https://www.dominos.jp/en/store/":
                        locs.append(lurl)
    website = "dominos.jp"
    typ = "<MISSING>"
    country = "JP"
    for loc in locs:
        logger.info(loc)
        store = loc.rsplit("/", 1)[1]
        name = ""
        raw_address = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" - ")[0].replace("&#39;", "'")
            if 'id="store-lat" value="' in line2:
                lat = line2.split('id="store-lat" value="')[1].split('"')[0]
            if 'id="store-lon" value="' in line2:
                lng = line2.split('id="store-lon" value="')[1].split('"')[0]
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'href="http://maps.google.com/maps/' in line2 and add == "":
                g = next(lines)
                g = g.strip().replace("\t", "").replace("\n", "").replace("\r", "")
                raw_address = g.strip()
                formatted_addr = parse_address_intl(raw_address)
                add = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    add = add + ", " + formatted_addr.street_address_2
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zc = formatted_addr.postcode if formatted_addr.postcode else "<MISSING>"
            if "～" in line2 and "～～this" not in line2:
                hours = line2.split(">")[1].split("<")[0].replace("～", "-")
        if "," in raw_address:
            add = raw_address.split(",")[0].strip()
        else:
            add = "<MISSING>"
        if (
            "a" not in add
            and "e" not in add
            and "i" not in add
            and "o" not in add
            and "u" not in add
            and "MISSING" not in add
        ):
            add = (
                raw_address.split(",")[0].strip()
                + " "
                + raw_address.split(",")[1].strip()
            )
        if "Tokyo" in raw_address:
            city = "Tokyo"
        zc = "<MISSING>"
        items = raw_address.split(",")
        for item in items:
            if "-Shi" in item or "-shi" in item:
                city = item.strip()
        if int(lat.split(".")[0]) < -90 or int(lat.split(".")[0]) > 90:
            lat = "<MISSING>"
            lng = "<MISSING>"
        if lng == "-99":
            lat = "<MISSING>"
            lng = "<MISSING>"
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
            raw_address=raw_address,
            hours_of_operation=hours,
        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
