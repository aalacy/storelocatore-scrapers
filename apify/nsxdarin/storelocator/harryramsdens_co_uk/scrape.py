from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("harryramsdens_co_uk")


def fetch_data():
    urls = [
        "Pitstop|https://www.harryramsdens.co.uk/locations?service=3",
        "Restaurant|https://www.harryramsdens.co.uk/locations?service=1",
        "Takeaway|https://www.harryramsdens.co.uk/locations?service=2",
    ]
    website = "harryramsdens.co.uk"
    country = "GB"
    locs = []
    allurls = []
    typ = "<MISSING>"
    for url in urls:
        r = session.get(url.split("|")[1], headers=headers)
        for line in r.iter_lines():
            if 'class="list-group-item-action">' in line:
                curl = line.split('href="')[1].split('"')[0]
                if curl not in allurls:
                    allurls.append(curl)
                    locs.append(url.split("|")[0] + "|" + curl)
    for loc in locs:
        lurl = loc.split("|")[1]
        typ = loc.split("|")[0]
        logger.info(lurl)
        phone = "<MISSING>"
        hours = ""
        state = "<MISSING>"
        store = "<MISSING>"
        r = session.get(lurl, headers=headers)
        dc = 0
        for line in r.iter_lines():
            if "<title>" in line:
                name = line.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if '<span class="office-hours__item-label"' in line:
                day = line.split('">')[1].split("<")[0]
                dc = dc + 1
            if '<span class="office-hours__item-slots">' in line:
                hrs = (
                    day
                    + line.split('<span class="office-hours__item-slots">')[1].split(
                        "<"
                    )[0]
                )
                if dc <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
            if '<span class="address-line1">' in line:
                add = line.split('<span class="address-line1">')[1].split("<")[0]
            if 'class="address-line2">' in line:
                add = add + " " + line.split('class="address-line2">')[1].split("<")[0]
                add = add.strip()
            if 'class="locality">' in line:
                city = line.split('class="locality">')[1].split("<")[0]
            if 'class="postal-code">' in line:
                zc = line.split('class="postal-code">')[1].split("<")[0]
            if '<a href="tel:' in line:
                phone = line.split('<a href="tel:')[1].split('"')[0]
            if '<meta property="latitude" content="' in line:
                lat = line.split('<meta property="latitude" content="')[1].split('"')[0]
            if '<meta property="longitude" content="' in line:
                lng = line.split('<meta property="longitude" content="')[1].split('"')[
                    0
                ]
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
