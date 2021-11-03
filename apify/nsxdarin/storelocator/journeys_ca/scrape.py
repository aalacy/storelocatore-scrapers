from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("journeys_ca")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.journeys.ca/stores"
    states = []
    locs = []
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if (
            '<option value="' in line
            and '<option value=""' not in line
            and "miles" not in line
        ):
            states.append(line.split('<option value="')[1].split('"')[0])
    for state in states:
        logger.info(("Pulling Province %s..." % state))
        findurl = (
            "https://www.journeys.ca/stores?StateOrProvince="
            + state
            + "&PostalCode=&MileRadius=&Latitude=&Longitude=&Mode=search"
        )
        r2 = session.get(findurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'class="store-name">' in line2:
                sname = line2.split('">')[1].split("#")[0].strip()
                surl = line2.split('href="')[1].split('"')[0]
                if surl not in locs:
                    locs.append(surl + "|" + sname)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        r2 = session.get(loc.split("|")[0], headers=headers)
        name = loc.split("|")[1]
        purl = loc.split("|")[0]
        typ = loc.split("|")[1]
        if r2.encoding is None:
            r2.encoding = "utf-8"
        AFound = False
        lines = r2.iter_lines(decode_unicode=True)
        website = "journeys.ca"
        add = ""
        hours = ""
        for line2 in lines:
            if '<p itemprop="streetAddress">' in line2:
                AFound = True
            if AFound and '<span itemprop="addressLocality">' in line2:
                website = "journeys.ca"
                AFound = False
                city = line2.split('span itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
                country = "CA"
            if AFound and "<p item" not in line2 and "</p>" in line2 and "<p>" in line2:
                add = add + " " + line2.split("<p>")[1].split("<")[0]
            if "Store ID', '" in line2:
                store = line2.split("Store ID', '")[1].split("'")[0]
            if '<span itemprop="telephone">' in line2:
                phone = line2.split('<span itemprop="telephone">')[1].split("<")[0]
            if '<span itemprop="openingHours"' in line2:
                hrs = (
                    line2.split('<span itemprop="openingHours"')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "</html>" in line2:
                lat = "<MISSING>"
                lng = "<MISSING>"
        add = add.strip()
        name = "JOURNEYS #" + store
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
