from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("westfield_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.westfield.com"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "westfield.com"
    for line in r.iter_lines(decode_unicode=True):
        if '<h2 class="tile-centre__header u-font--flama"> <a href="/' in line:
            items = line.split(
                '<h2 class="tile-centre__header u-font--flama"> <a href="/'
            )
            for item in items:
                if 'class="js-centre-name" data-track="click center tile"' in item:
                    city = (
                        item.split('<div class="tile-centre__subtitle">')[1]
                        .split(",")[0]
                        .strip()
                    )
                    locs.append(
                        "https://www.westfield.com/" + item.split('"')[0] + "|" + city
                    )
    for loc in locs:
        logger.info((loc.split("|")[0]))
        r2 = session.get(loc.split("|")[0], headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        typ = "Center"
        store = "<MISSING>"
        name = ""
        add = ""
        city = loc.split("|")[1]
        state = ""
        zc = ""
        country = "US"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = "<MISSING>"
        for line2 in r2.iter_lines(decode_unicode=True):
            if 'name="title" content="' in line2:
                name = line2.split('name="title" content="')[1].split('"')[0]
            if '<div class="content"><a href="/' in line2:
                info = line2.split('<div class="content"><a href="/')[1]
                addinfo = info.split('">')[1].split("<")[0].strip()
                zc = addinfo.rsplit(" ", 1)[1]
                state = addinfo.rsplit(" ", 2)[1].split(" ")[0]
                phone = info.split('<a href="tel:')[1].split('"')[0]
                add = addinfo.split(city)[0].strip()
        loc2 = loc.split("|")[0] + "/access"
        r3 = session.get(loc2, headers=headers)
        if r3.encoding is None:
            r3.encoding = "utf-8"
        for line3 in r3.iter_lines(decode_unicode=True):
            if '<span class="date">' in line3:
                items = line3.split('<span class="date">')
                for item in items:
                    if '<span class="schedule">' in item:
                        hrs = (
                            item.split("<")[0]
                            + ": "
                            + item.split('<span class="schedule">')[1].split("<")[0]
                        )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if add != "":
            if "annapolis" in loc.split("|")[0]:
                add = "2002 Annapolis Mall"
                city = "Annapolis"
                state = "MD"
                zc = "21401"
            if " (" in add:
                add = add.split(" (")[0]
            if "brandon" in loc.split("|")[0]:
                add = "459 Brandon Town Center"
                city = "Brandon"
                state = "FL"
                zc = "33511"
            if "valencia" in add.split("|")[0]:
                add = "24201 West Valencia Blvd Suite 150"
                city = "Valencia"
                state = "CA"
                zc = "91355"
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
