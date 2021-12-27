from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("pandaexpress_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.pandaexpress.com/sitemap.xml"
    mexico = [
        "bn",
        "c1",
        "df",
        "du",
        "gt",
        "i1",
        "ka",
        "l1",
        "m1",
        "mx",
        "o1",
        "qr",
        "s1",
        "sc",
        "sa",
        "se",
        "t1",
    ]
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if (
            " <loc>https://www.pandaexpress.com/userlocation/" in line
            and "/  /" not in line
        ):
            lurl = line.split("<loc>")[1].split("<")[0]
            st = lurl.split("https://www.pandaexpress.com/userlocation/")[1].split("/")[
                1
            ]
            if st not in mexico:
                locs.append(lurl)
    logger.info(("Found %s Locations." % str(len(locs))))
    canada = [
        "AB",
        "BC",
        "MB",
        "QC",
        "NB",
        "NL",
        "NS",
        "ON",
        "PE",
        "SK",
        "YT",
        "NU",
        "NT",
    ]
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = (
            loc.split("https://www.pandaexpress.com/userlocation/")[1]
            .split("/")[1]
            .upper()
        )
        if state in canada:
            country = "CA"
        else:
            country = "US"
        zc = ""
        phone = ""
        website = "pandaexpress.com"
        typ = "Restaurant"
        hours = ""
        lat = ""
        lng = ""
        store = loc.split("https://www.pandaexpress.com/userlocation/")[1].split("/")[0]
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if '<h1 class="title">' in line2:
                name = (
                    line2.split('<h1 class="title">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("&amp;", "&")
                    .replace("&#39;", "'")
                )
            if "var store = { lat: " in line2:
                lat = line2.split("var store = { lat: ")[1].split(",")[0].strip()
                lng = line2.split("lng:")[1].split("}")[0].strip()
            if '<span class="address">' in line2:
                add = (
                    line2.split('<span class="address">')[1]
                    .split("<")[0]
                    .strip()
                    .replace("&amp;", "&")
                    .replace("&#39;", "'")
                )
                city = (
                    line2.split("<br>")[1]
                    .split(",")[0]
                    .strip()
                    .replace("&amp;", "&")
                    .replace("&#39;", "'")
                )
                zc = (
                    line2.split("<br>")[1]
                    .strip()
                    .split(",")[1]
                    .strip()
                    .split(" ", 1)[1]
                    .split("<")[0]
                    .replace("&amp;", "&")
                    .replace("&#39;", "'")
                )
            if "<span>Phone:</span>" in line2:
                phone = line2.split("<span>Phone:</span>")[1].split("<")[0].strip()
            if '<span class="day"' in line2:
                if hours == "":
                    hours = (
                        line2.split('<span class="day"')[1]
                        .split('">')[1]
                        .split("<")[0]
                        .strip()
                        + ": "
                    )
                else:
                    hours = (
                        hours
                        + "; "
                        + line2.split('<span class="day"')[1]
                        .split('">')[1]
                        .split("<")[0]
                        .strip()
                        + ": "
                    )
            if '<span class="hour"' in line2:
                hours = (
                    hours
                    + line2.split('<span class="hour"')[1]
                    .split('">')[1]
                    .split("<")[0]
                    .strip()
                )
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if add != "":
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
