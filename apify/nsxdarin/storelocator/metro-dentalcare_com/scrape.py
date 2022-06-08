from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():
    url = "https://www.metro-dentalcare.com/"
    r = session.get(url, headers=headers)
    website = "metro-dentalcare.com"
    typ = "Office"
    country = "US"
    lines = r.iter_lines()
    store = "<MISSING>"
    for line in lines:
        if '<h3 class="office-card__title">' in line:
            name = line.split('<h3 class="office-card__title">')[1].split("<")[0]
        if 'ss="office-card__address">' in line:
            g = next(lines)
            h = next(lines)
            add = g.split(">")[1].split("<")[0].strip()
            csz = h.split(">")[1].split("<")[0].strip()
            city = csz.split(",")[0]
            state = csz.split(",")[1].strip().split(" ")[0]
            zc = csz.rsplit(" ", 1)[1]
        if '<a class="office-card__phone" href="tel:' in line:
            phone = (
                line.split('<a class="office-card__phone" href="tel:')[1]
                .split(">")[1]
                .split("<")[0]
            )
        if '<a class="office-card__website" href="' in line:
            loc = line.split('<a class="office-card__website" href="')[1].split('"')[0]
            hours = "<MISSING>"
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
                hours_of_operation=hours,
            )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
