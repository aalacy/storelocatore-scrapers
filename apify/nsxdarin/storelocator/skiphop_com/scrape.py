from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()

user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.162 Safari/537.36"
headers = {"User-Agent": user_agent}


def fetch_data():
    url = "https://www.skiphop.com/skiphop-stores-110818.html"
    r = session.get(url, headers=headers)
    website = "skiphop.com"
    country = "US"
    loc = "https://www.skiphop.com/skiphop-stores-110818.html"
    SFound = False
    lat = "<MISSING>"
    lng = "<MISSING>"
    phone = "<MISSING>"
    typ = ""
    hours = "<MISSING>"
    store = "<MISSING>"
    lines = r.iter_lines()
    sid = 0
    for line in lines:
        if '<ul class="storeList"' in line:
            SFound = True
        if SFound and "</ul>" in line:
            SFound = False
        if SFound and "<li" in line:
            sid = sid + 1
            store = str(sid)
            g = next(lines)
            h = next(lines)
            i = next(lines)
            name = g.split("<")[0]
            add = h.split("<")[0]
            city = i.split(",")[0]
            state = i.split(",")[1].strip().split(" ")[0]
            zc = i.split("<")[0].strip().rsplit(" ", 1)[1]
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
