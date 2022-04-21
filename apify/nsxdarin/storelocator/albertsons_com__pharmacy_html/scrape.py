from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("albertsons_com__pharmacy_html")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    cities = []
    url = "https://local.pharmacy.albertsons.com/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '"links_directory" href="' in line:
            items = line.split('"links_directory" href="')
            for item in items:
                if 'data-count="(' in item:
                    count = item.split('data-count="(')[1].split(")")[0]
                    lurl = "https://local.pharmacy.albertsons.com/" + item.split('"')[0]
                    if count == "1":
                        locs.append(lurl)
                    else:
                        states.append(lurl)
    for state in states:
        logger.info(("Pulling State %s..." % state))
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'data-ya-track="links_directory" href="' in line2:
                items = line2.split('data-ya-track="links_directory" href="')
                for item in items:
                    if 'data-count="(' in item:
                        count = item.split('data-count="(')[1].split(")")[0]
                        lurl = (
                            "https://local.pharmacy.albertsons.com/"
                            + item.split('"')[0]
                        )
                        if count == "1":
                            locs.append(lurl)
                        else:
                            cities.append(lurl)
    for city in cities:
        logger.info(("Pulling City %s..." % city))
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            if '<a class="Teaser-titleLink" href="../' in line2:
                items = line2.split('<a class="Teaser-titleLink" href="../')
                for item in items:
                    if 'data-ya-track="storename_directory">' in item:
                        lurl = (
                            "https://local.pharmacy.albertsons.com/"
                            + item.split('"')[0]
                        )
                        locs.append(lurl)
    for loc in locs:
        logger.info("Pulling Location %s..." % loc)
        website = "albertsons.com/pharmacy.html"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        store = ""
        phone = ""
        lat = ""
        lng = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<div class="Heading--lead ContentBanner-title">' in line2:
                name = line2.split('<div class="Heading--lead ContentBanner-title">')[
                    1
                ].split("<")[0]
            if '"normalHours":[' in line2:
                days = (
                    line2.split('"normalHours":[')[1].split(']},"')[0].split('"day":"')
                )
                for day in days:
                    if "isClosed" in day:
                        if 'isClosed":true' in day:
                            hrs = day.split('"')[0] + ": Closed"
                        else:
                            hrs = (
                                day.split('"')[0]
                                + ": "
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
            if add == "" and 'address-street-1">' in line2:
                add = line2.split('address-street-1">')[1].split("<")[0]
                city = line2.split('"c-address-city">')[1].split("<")[0]
                state = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('"postalCode">')[1].split("<")[0]
                phone = line2.split('id="phone-main">')[1].split("<")[0]
            if '<meta itemprop="latitude" content="' in line2:
                lat = line2.split('<meta itemprop="latitude" content="')[1].split('"')[
                    0
                ]
                lng = line2.split('<meta itemprop="longitude" content="')[1].split('"')[
                    0
                ]
            if (
                store == ""
                and 'href="https://www.albertsons.com/set-store.html?storeId=' in line2
            ):
                store = line2.split(
                    'href="https://www.albertsons.com/set-store.html?storeId='
                )[1].split("&")[0]
        if hours == "":
            hours = "<MISSING>"
        add = add.replace("&#39;", "'")
        name = name.replace("&#39;", "'")
        hours = hours.replace(": 1000", ": 10:00 AM ")
        hours = hours.replace(": 900", ": 9:00 AM ")
        hours = hours.replace(": 800", ": 8:00 AM ")
        hours = hours.replace("-2000", "- 8:00 PM")
        hours = hours.replace("-2100", "- 9:00 PM")
        hours = hours.replace("-2200", "- 10:00 PM")
        hours = hours.replace("-2300", "- 11:00 PM")
        hours = hours.replace("-1900", "- 7:00 PM")
        hours = hours.replace("-1800", "- 6:00 PM")
        hours = hours.replace("-1700", "- 5:00 PM")
        hours = hours.replace("-1600", "- 4:00 PM")
        name = name.replace("&amp;", "&").replace("&Amp;", "&").replace("&amp", "&")
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
