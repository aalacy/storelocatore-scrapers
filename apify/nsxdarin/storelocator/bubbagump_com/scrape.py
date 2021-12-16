from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    r = session.get("https://www.bubbagump.com/store-locator/", headers=headers)
    lines = r.iter_lines()
    country = "US"
    website = "bubbagump.com"
    typ = "Restaurant"
    hours = "<MISSING>"
    for line in lines:
        if '{"name": "' in line:
            line = line.replace('"categories": [{"name":', "")
            items = line.split('"name": "')
            for item in items:
                if '"slug": "' in item:
                    store = "<MISSING>"
                    purl = (
                        "https://www.bubbagump.com/location/"
                        + item.split('"slug": "')[1].split('"')[0]
                    )
                    name = item.split('"')[0]
                    lat = item.split('"lat": "')[1].split('"')[0]
                    lng = item.split('"lng": "')[1].split('"')[0]
                    phone = item.split('"phone_number": "')[1].split('"')[0]
                    add = item.split('"street": "')[1].split('"')[0]
                    city = item.split('"city": "')[1].split('"')[0]
                    state = item.split('"state": "')[1].split('"')[0]
                    zc = item.split('"postal_code": "')[1].split('"')[0]
                    hours = (
                        item.split('"hours": "')[1]
                        .split('"')[0]
                        .replace("\\u003cbr/\\u003e", "; ")
                    )
                    hours = hours.replace("\\u003cp\\u003e", "")
                    if "\\u" in hours:
                        hours = hours.split("\\u")[0]
                    if state == "UK":
                        state = "<MISSING>"
                        country = "UK"
                    if state == "AB":
                        country = "CA"
                    if ", JP" in name:
                        country = "JP"
                    if "CNMI" in name:
                        country = "US"
                    if ", QR" in name:
                        country = "MX"
                    if "QA" in name:
                        country = "QA"
                    if ", CN" in name:
                        country = "CN"
                    if "Kuta" in name:
                        country = "ID"
                    if ", JL" in name:
                        country = "MX"
                    name = name.replace("\\u0026", "&")
                    add = add.replace("\\u0026", "&")
                    if country == "CN" or country == "QA":
                        state = "<MISSING>"
                        zc = "<MISSING>"
                    if "Baltimore" in city:
                        hours = "Sunday - Thursday: 11:30 AM - 9:00 PM; Friday - Saturday: 11:30 AM - 10:00 PM"
                    if "Orlando" in city:
                        hours = "SUN - SAT: 11:00 AM - 11:00 PM"
                    if "beijing" in purl:
                        phone = "010-13651001283"
                        hours = "<MISSING>"
                    if "Coming" not in name:
                        yield SgRecord(
                            locator_domain=website,
                            page_url=purl,
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
