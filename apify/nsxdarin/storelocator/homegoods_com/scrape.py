from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("homegoods_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.homegoods.com/all-stores"
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<h5>" in line:
            sname = line.split("<h5>")[1].split("<")[0].strip()
        if '<a class="arrow-link" href="' in line:
            lurl = "https://www.homegoods.com" + line.split('href="')[1].split('"')[0]
            locs.append(lurl + "|" + sname)
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        CS = False
        loc = loc.replace("&#39;", "'")
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        website = "homegoods.com"
        typ = "Store"
        r2 = session.get(loc.split("|")[0], headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if "New store opening on" in line2:
                CS = True
            if "<h2>" in line2:
                g = next(lines)
                h = next(lines)
                if "<" not in g:
                    g = h
                    h = next(lines)
                if "," not in h:
                    h = next(lines)
                add = g.split("<")[0].strip().replace("\t", "")
                city = h.split(",")[0].strip().replace("\t", "")
                state = h.split(",")[1].strip().split(" ")[0]
                zc = h.rsplit(" ", 1)[1].strip().replace("\r", "").replace("\n", "")
            if '"Phone Number:Call">' in line2:
                phone = line2.split('"Phone Number:Call">')[1].split("<")[0].strip()
                g = next(lines)
                hours = (
                    g.split("<")[0]
                    .strip()
                    .replace("\r", "")
                    .replace("\n", "")
                    .replace("\t", "")
                )
        country = "US"
        store = loc.rsplit("/", 1)[1]
        lat = "<MISSING>"
        lng = "<MISSING>"
        name = loc.split("|")[1]
        if name == "":
            name = "Home Goods"
        if "|" in store:
            store = store.split("|")[0]
        add = add.replace("&#39;", "'")
        city = city.replace("&#39;", "'")
        name = name.replace("&#39;", "'")
        if CS is False:
            yield SgRecord(
                locator_domain=website,
                page_url=loc.split("|")[0],
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
