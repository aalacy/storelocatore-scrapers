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
    url = "https://www.bpgroupusa.com/OurLocations.html"
    r = session.get(url, headers=headers)
    LFound = True
    LocFound = False
    website = "bpgroupusa.com"
    name = "<MISSING>"
    add = "<MISSING>"
    loc = "https://www.bpgroupusa.com/OurLocations.html"
    city = "<MISSING>"
    state = "<MISSING>"
    zc = "<MISSING>"
    phone = "<MISSING>"
    hours = "<MISSING>"
    country = "US"
    typ = "Restaurant"
    snum = 0
    lat = "<MISSING>"
    lng = "<MISSING>"
    lines = r.iter_lines()
    for line in lines:
        if 'id="canada">' in line:
            country = "CA"
        if 'id="japan">' in line:
            country = "JP"
        if '<div class="row ourlocations-title" id="china">' in line:
            LFound = False
        if (
            LFound
            and '<div class="row ourlocations-row">' in line
            and "<!--" not in line
        ):
            LocFound = True
        if "<!--" in line and "-->" not in line:
            LocFound = False
            next(lines)
            next(lines)
        if LocFound and "PM" in line:
            snum = snum + 1
            store = str(snum)
            LocFound = False
            hours = (
                line.split("<br>")[0]
                .strip()
                .replace("\t", "")
                .replace("<br />", "")
                .replace("  ", " ")
            )
            zc = zc.replace("JAPAN", "").strip()
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
        if LocFound and '<div class="ourlocations-box">' in line:
            name = next(lines).split(">")[1].split("<")[0]
            addline = next(lines)
            while "<br>" not in addline:
                addline = next(lines)
            add = addline.split("<")[0].strip().replace("\t", "")
            csz = next(lines)
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ", 1)[0].replace(".", "")
            zc = (
                csz.split(",")[1]
                .strip()
                .split(" ", 1)[1]
                .split("<")[0]
                .replace("OJ8", "0J8")
            )
        if (
            LocFound
            and '<li><a href="https://www.google.com/maps/dir/?api=1&destination='
            in line
        ):
            lat = line.split(
                '<li><a href="https://www.google.com/maps/dir/?api=1&destination='
            )[1].split(",")[0]
            lng = (
                line.split(
                    '<li><a href="https://www.google.com/maps/dir/?api=1&destination='
                )[1]
                .split(",")[1]
                .split('"')[0]
            )
        if '<li><a href="callto:' in line:
            phone = line.split('<li><a href="callto:')[1].split('"')[0]
    zc = zc.replace("JAPAN", "").strip()
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
