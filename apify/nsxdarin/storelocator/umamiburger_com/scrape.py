from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("umamiburger_com")

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.umamiburger.com/dine-in-locations"
    locs = []
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'tabName":null,"url":"' in line:
            items = line.split('tabName":null,"url":"')
            for item in items:
                stub = item.split('"')[0]
                if (
                    "<script" not in stub
                    and "contact" not in stub
                    and "catering" not in stub
                    and "shakes-" not in stub
                    and "dine-in" not in stub
                    and "terms" not in stub
                    and "menu" not in stub
                ):
                    if (
                        "privacy" not in stub
                        and "order" not in stub
                        and "about" not in stub
                        and "pick" not in stub
                        and "events" not in stub
                        and len(stub) >= 3
                    ):
                        locs.append("https://www.umamiburger.com" + stub)
    for loc in locs:
        if " " not in loc:
            logger.info(("Pulling Location %s..." % loc))
            r2 = session.get(loc, headers=headers)
            website = "www.umamiburger.com"
            typ = "Restaurant"
            store = "<MISSING>"
            add = ""
            zc = ""
            state = ""
            city = ""
            country = "US"
            name = ""
            phone = ""
            hours = ""
            lat = ""
            lng = ""
            CS = False
            TC = False
            for line2 in r2.iter_lines():
                if "Temporarily Closed" in line2:
                    TC = True
                if "- Coming Soon<" in line2:
                    CS = True
                if "><h4>" in line2 and add == "":
                    name = line2.split("><h4>")[1].split("<")[0]
                    add = (
                        line2.split("<h4>")[1]
                        .split("<span>")[1]
                        .split("</span")[0]
                        .replace("<!-- -->", "")
                        .strip()
                    )
                    csz = line2.split("<h4>")[1].split("<br />")[1].split("<")[0]
                    city = csz.split(",")[0]
                    try:
                        zc = csz.rsplit(" ", 1)[1]
                    except:
                        zc = "<MISSING>"
                    try:
                        state = csz.split(",")[1].strip().split(" ")[0]
                    except:
                        state = "<MISSING>"
                    add = (
                        add.replace("<!-- -->", " ")
                        .replace("  ", " ")
                        .replace("  ", " ")
                    )
                if '"lat":' in line2:
                    lat = line2.rsplit('"lat":', 1)[1].split(",")[0]
                    lng = line2.rsplit('"lng":', 1)[1].split(",")[0]
                if '<p><a href="tel:' in line2:
                    phone = line2.split('<p><a href="tel:')[1].split('"')[0]
                if "<strong>Temporarily Closed" in line2:
                    hours = "Temporarily Closed"
                if "Hours</h4>" in line2:
                    days = (
                        line2.split("Hours</h4>")[1]
                        .split("</div></div></div>")[0]
                        .split('"hours-day">')
                    )
                    for day in days:
                        if '<span class="hours-time"> <span>' in day:
                            hrs = (
                                day.split("<")[0]
                                + ": "
                                + day.split('<span class="hours-time"> <span>')[1]
                                .split("</span></span>")[0]
                                .replace("<!-- -->", "")
                                .replace("  ", " ")
                                .replace("  ", " ")
                            )
                            if hours == "":
                                hours = hrs
                            else:
                                hours = hours + "; " + hrs
            if phone == "":
                phone = "<MISSING>"
            add = add.strip().replace("  ", " ").replace("  ", " ")
            if TC:
                hours = "Temporarily Closed"
            if CS is False:
                if city != "<MISSING>" and "www.umamiburger.com/careers" not in loc:
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
