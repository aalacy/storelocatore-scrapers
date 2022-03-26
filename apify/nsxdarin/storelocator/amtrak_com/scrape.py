from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
import time

logger = SgLogSetup().get_logger("amtrak_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    canada = [
        "SK",
        "ON",
        "PQ",
        "QC",
        "AB",
        "MB",
        "BC",
        "YT",
        "NS",
        "NF",
        "NL",
        "PEI",
        "PE",
    ]
    url = "https://www.amtrak.com/sitemap.xml"
    session = SgRequests()
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    for line in r.iter_lines(decode_unicode=True):
        if "<loc>https://www.amtrak.com/stations/" in line:
            items = line.split("<loc>https://www.amtrak.com/stations/")
            for item in items:
                if "<?xml" not in item:
                    lurl = (
                        "https://www.amtrak.com/content/amtrak/en-us/stations/"
                        + item.split("<")[0]
                    )
                    locs.append(lurl)
        if "<loc>https://beta.amtrak.com/stations/" in line:
            items = line.split("<loc>https://beta.amtrak.com/stations/")
            for item in items:
                if "<?xml" not in item:
                    lurl = (
                        "https://beta.amtrak.com/content/amtrak/en-us/stations/"
                        + item.split("<")[0]
                    )
                    locs.append(lurl)
    for loc in locs:
        time.sleep(2)
        logger.info(("Pulling Location %s..." % loc))
        website = "amtrak.com"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        lat = "<MISSING>"
        lng = "<MISSING>"
        phone = "215-856-7924"
        store = loc.rsplit("/", 1)[1].split(".")[0]
        lurl = "https://www.amtrak.com/content/amtrak/en-us/stations/" + store + ".html"
        session = SgRequests()
        r2 = session.get(lurl, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if '<h1 class="hero-banner-and-info__card_info-title">' in line2:
                name = line2.split(
                    '<h1 class="hero-banner-and-info__card_info-title">'
                )[1].split("<")[0]
            if add == "" and 'ard_block-address">' in line2:
                add = line2.split('ard_block-address">')[1].split("<")[0]
            if add != "" and 'ard_block-address">' in line2 and "-->" not in line2:
                if add not in line2 and ", " in line2:
                    csz = line2.split('card_block-address">')[1].split("<")[0].strip()
                    city = csz.split(",")[0]
                    state = csz.split(",")[1].strip().split(" ")[0]
                    if state not in canada:
                        zc = csz.rsplit(" ", 1)[1]
                    else:
                        zc = csz.rsplit(" ", 2)[1] + " " + csz.rsplit(" ", 1)[1]
            if 'station-type">' in line2:
                typ = line2.split('station-type">')[1].split("<")[0]
            if "maps/dir//" in line2:
                lat = line2.split("maps/dir//")[1].split(",")[0]
                lng = line2.split("maps/dir//")[1].split(",")[1].split('"')[0]
        hurl = (
            "https://www.amtrak.com/content/amtrak/en-us/stations/"
            + store.lower()
            + ".stationTabContainer."
            + store.upper()
            + ".json"
        )
        r3 = session.get(hurl, headers=headers)
        if r3.encoding is None:
            r3.encoding = "utf-8"
        for line3 in r3.iter_lines(decode_unicode=True):
            if '"type":"stationhours","rangeData":[{' in line3:
                days = (
                    line3.split('"type":"stationhours","rangeData":[{')[1]
                    .split("}]}]},")[0]
                    .split('"day":"')
                )
                for day in days:
                    if "timeSlot" in day:
                        hrs = (
                            day.split('"')[0]
                            + ": "
                            + day.split('"timeSlot":"')[1].split('"')[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if state in canada:
            country = "CA"
        if "(" in typ:
            typ = typ.split("(")[0].strip()
        if add != "":
            yield SgRecord(
                locator_domain=website,
                page_url=lurl,
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
