from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("tacobell_co_uk")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://locations.tacobell.co.uk/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"alternate" hreflang="en-GB" href="' in line:
            lurl = line.split('"alternate" hreflang="en-GB" href="')[1].split('"')[0]
            if lurl.count("/") == 4:
                locs.append(lurl)
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc))
        website = "tacobell.co.uk"
        typ = "Restaurant"
        hours = ""
        country = "GB"
        name = ""
        state = ""
        zc = ""
        city = ""
        store = "<MISSING>"
        add = ""
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if 'og:title" content="' in line2:
                name = line2.split('og:title" content="')[1].split(" |")[0]
            if '<span class="c-address-street-1">' in line2:
                add = (
                    line2.split('<span class="c-address-street-1">')[1]
                    .split("<")[0]
                    .strip()
                )
                try:
                    add = (
                        add
                        + " "
                        + line2.split('<span class="c-address-street-2">')[1].split(
                            "<"
                        )[0]
                    )
                    add = add.strip()
                except:
                    pass
                city = line2.split('<span class="c-address-city">')[1].split("<")[0]
                state = "<MISSING>"
                zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                try:
                    phone = (
                        line2.split('itemprop="telephone" id="phone-main">')[1]
                        .split("<")[0]
                        .strip()
                    )
                except:
                    phone = ""
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
                if (
                    '<tr class="c-hours-details-row is-holiday js-day-of-week-row highlight-text" data-day-of-week-start-index="1" data-day-of-week-end-index="1"><td class="c-hours-details-row-day">Mon</td><td class="c-hours-details-row-intervals">Closed</td>'
                    in line2
                ):
                    hours = "Closed"
                else:
                    try:
                        hours = (
                            "Mon: "
                            + line2.split('<td class="c-hours-details-row-day">Mon')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Mon')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = "Mon: Closed"
                    try:
                        hours = (
                            hours
                            + "; Tue: "
                            + line2.split('<td class="c-hours-details-row-day">Tue')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Tue')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Tue: Closed"
                    try:
                        hours = (
                            hours
                            + "; Wed: "
                            + line2.split('<td class="c-hours-details-row-day">Wed')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Wed')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Wed: Closed"
                    try:
                        hours = (
                            hours
                            + "; Thu: "
                            + line2.split('<td class="c-hours-details-row-day">Thu')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Thu')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Thu: Closed"
                    try:
                        hours = (
                            hours
                            + "; Fri: "
                            + line2.split('<td class="c-hours-details-row-day">Fri')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Fri')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Fri: Closed"
                    try:
                        hours = (
                            hours
                            + "; Sat: "
                            + line2.split('<td class="c-hours-details-row-day">Sat')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Sat')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Sat: Closed"
                    try:
                        hours = (
                            hours
                            + "; Sun: "
                            + line2.split('<td class="c-hours-details-row-day">Sun')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-open">'
                            )[1]
                            .split("<")[0]
                            + "-"
                            + line2.split('<td class="c-hours-details-row-day">Sun')[1]
                            .split(
                                '<span class="c-hours-details-row-intervals-instance-close">'
                            )[1]
                            .split("<")[0]
                        )
                    except:
                        hours = hours + "; Sun: Closed"
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if " - " in name:
            name = name.split(" - ")[0]
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
