# -*- coding: cp1252 -*-
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import re

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.dallasbbq.com"
    locs = []
    r = session.get(url, headers=headers, verify=False)
    Found = True
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if ">Locations &amp; Menus</a>" in line and len(locs) == 0:
            Found = True
        if "Gift Cards" in line:
            Found = False
        if (
            Found
            and '<a href="/' in line
            and "/drinks" not in line
            and "gift-" not in line
        ):
            lurl = "https://www.dallasbbq.com" + line.split('href="')[1].split('"')[0]
            if lurl != "https://www.dallasbbq.com/":
                locs.append(lurl)
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        website = "dallasbbq.com"
        typ = "Restaurant"
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        Found = False
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("&m")[0].strip()
            if "&quot;addressLine1&quot;:&quot;" in line2:
                add = line2.split("&quot;addressLine1&quot;:&quot;")[1].split("&quot")[
                    0
                ]
                csz = line2.split("&quot;addressLine2&quot;:&quot;")[1].split("&quot")[
                    0
                ]
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip()
                zc = csz.split(",")[2].strip()
                lat = line2.split("markerLat&quot;:")[1].split(",")[0]
                lng = line2.split("markerLng&quot;:")[1].split("&")[0]
            if "Phone</strong><br>" in line2:
                phone = line2.split("Phone</strong><br>")[1].split("<")[0]
            if "PHONE</strong><br>" in line2:
                phone = line2.split("PHONE</strong><br>")[1].split("<")[0]
            if "Hours</strong><br>" in line2:
                hours = line2.split("Hours</strong><br>")[1].split("<")[0]
            if "HOURS</strong><br>" in line2:
                hours = line2.split("HOURS</strong><br>")[1].split("<")[0]
            if "HOURS</strong><br><em>" in line2:
                hours = line2.split("HOURS</strong><br><em>")[1].split("</p")[0]
        country = "US"
        store = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace(" • ", "; ").replace("&amp;", "&")
        if "FOR TAKE" in hours:
            hours = hours.split("FOR TAKE")[0].strip()
        cleanr = re.compile("<.*?>")
        hours = re.sub(cleanr, "", hours)
        hours = hours.replace(" ;", ";")
        if "downtown-brooklyn" in loc:
            phone = "(718) 643-5700"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
