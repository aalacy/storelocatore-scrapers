from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("texasroadhouse_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.texasroadhouse.com/sitemap.xml"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://togo.texasroadhouse.com/location/" in line:
            items = line.split("<loc>https://togo.texasroadhouse.com/location/")
            for item in items:
                if 'version="1.0"' not in item:
                    lurl = (
                        "https://www.texasroadhouse.com/locations/" + item.split("<")[0]
                    )
                    lurl = lurl.replace("/menu", "")
                    locs.append(lurl)
    for loc in locs:
        try:
            r2 = session.get(loc, headers=headers)
            logger.info(loc)
            name = ""
            add = ""
            website = "texasroadhouse.com"
            country = "<MISSING>"
            add = ""
            store = "<MISSING>"
            city = ""
            typ = "<MISSING>"
            state = "<MISSING>"
            zc = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            phone = ""
            hours = ""
            lines = r2.iter_lines()
            for line2 in lines:
                if '"og:title" content="' in line2:
                    name = line2.split('"og:title" content="')[1].split('"')[0]
                    name = name.split("|")[0].strip()
                    state = name[-2:]
                if '<p class="store-address">' in line2:
                    add = next(lines).split(",")[0].strip().replace("\t", "")
                if 'href="https://google.com/maps/place/' in line2:
                    csz = (
                        line2.split('href="https://google.com/maps/place/')[1]
                        .split('"')[0]
                        .replace("%2C", ",")
                        .replace("%20", " ")
                    )
                    city = csz.split(",")[0].strip()
                    zc = csz.rsplit(" ", 1)[1]
                if 'store-telephone">' in line2:
                    phone = (
                        next(lines)
                        .split("</svg>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if "day :" in line2:
                    hrs = (
                        line2.strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                    hrs = hrs.replace("<strong>", "").replace("</strong>", "").strip()
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            if hours == "":
                hours = "<MISSING>"
            cname = (
                name.replace("-W,", ",")
                .replace("-E,", ",")
                .replace("-S,", ",")
                .replace("-N,", ",")
            )
            cname = cname.replace("-NE,", ",")
            cname = cname.replace("-NW,", ",")
            cname = cname.replace("-SE,", ",")
            cname = cname.replace("-SW,", ",")
            city = cname.split(",")[0]
            if add != "" and city != "<MISSING>":
                name = name.replace("\\u0027", "'")
                add = add.replace("\\u0027", "'")
                name = name.replace("\\/", "/")
                add = add.replace("\\/", "/")
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
