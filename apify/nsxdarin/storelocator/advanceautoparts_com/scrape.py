from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("advanceautoparts_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    urls = ["https://stores.advanceautoparts.com/"]
    states = []
    cities = []
    locs = [
        "https://www.carquest.com/stores/dc/washington/14461",
        "https://www.carquest.com/stores/dc/washington/6360",
    ]
    website = "advanceautoparts.com"
    typ = "<MISSING>"
    country = "<MISSING>"
    for url in urls:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if ' data-count="(' in item:
                        count = item.split(' data-count="(')[1].split(")")[0]
                        if count != "1":
                            states.append(
                                "https://stores.advanceautoparts.com/"
                                + item.split('"')[0].replace("..", "")
                            )
                        else:
                            locs.append(
                                "https://stores.advanceautoparts.com/"
                                + item.split('"')[0].replace("..", "")
                            )
    for state in states:
        surl = state.replace("https://stores.advanceautoparts.com/https", "https")
        logger.info("Pulling State %s..." % surl)
        r = session.get(surl, headers=headers)
        for line in r.iter_lines():
            if '<a class="Directory-listLink" href="' in line:
                items = line.split('<a class="Directory-listLink" href="')
                for item in items:
                    if 'data-ya-track="todirectory" data-count="(' in item:
                        count = item.split('data-ya-track="todirectory" data-count="(')[
                            1
                        ].split(")")[0]
                        if count != "1":
                            city_url = item.split('"')[0]
                            if "http" not in city_url:
                                city_url = (
                                    "https://stores.advanceautoparts.com/" + city_url
                                )
                                cities.append(city_url)
                            else:
                                cities.append(city_url)
                        else:
                            locs.append(
                                "https://stores.advanceautoparts.com/"
                                + item.split('"')[0].replace("..", "")
                            )
    for city in cities:
        curl = city.replace("https://stores.advanceautoparts.com/https", "https")
        if "carquest.com/stores/or/bend" in curl:
            curl = "https://stores.advanceautoparts.com/or/bend"
        logger.info("Pulling City %s..." % curl)
        r = session.get(curl, headers=headers)
        for line in r.iter_lines():
            if 'data-ya-track="page" href="..' in line:
                items = line.split('data-ya-track="page" href="..')
                for item in items:
                    if "Store Details" in item:
                        if "stores.advanceautoparts.com" in city:
                            lurl = "https://stores.advanceautoparts.com/" + item.split(
                                '"'
                            )[0].replace("..", "")
                        else:
                            lurl = "https://www.carquest.com/stores" + item.split('"')[
                                0
                            ].replace("..", "")
                        locs.append(lurl)
    for loc in locs:
        loc = (
            loc.replace("&#39;", "%27")
            .replace(".com//", ".com/")
            .replace("https://stores.advanceautoparts.com/https", "https")
        )
        logger.info("Pulling Location %s..." % loc)
        LFound = True
        tries = 0
        while LFound:
            try:
                LFound = False
                tries = tries + 1
                typ = "Advance Auto Parts"
                r = session.get(loc, headers=headers)
                name = ""
                add = ""
                city = ""
                state = ""
                zc = ""
                lat = ""
                lng = ""
                hours = ""
                country = ""
                phone = ""
                store = ""
                NFound = False
                for line in r.iter_lines():
                    if NFound is False and '"Nap-heading Heading Heading--h1">' in line:
                        NFound = True
                        name = (
                            line.split('"Nap-heading Heading Heading--h1"')[1]
                            .split(">")[1]
                            .split("<")[0]
                            .strip()
                            .replace("<span>", "")
                            .replace("  ", " ")
                        )
                    if '"store_id":"' in line:
                        store = line.split('"store_id":"')[1].split('"')[0]
                    if '"line1":"' in line and add == "":
                        add = line.split('"line1":"')[1].split('"')[0]
                        city = line.split(':{"city":"')[1].split('"')[0]
                        state = line.split(',"region":"')[1].split('"')[0]
                        zc = line.split('"postalCode":"')[1].split('"')[0]
                        country = line.split('"countryCode":"')[1].split('"')[0]
                        if '"line2":null' not in line:
                            add = add + " " + line.split('"line2":"')[1].split('"')[0]
                    if ',"mainPhone":{"' in line:
                        phone = (
                            line.split(',"mainPhone":{"')[1]
                            .split('"display":"')[1]
                            .split('"')[0]
                        )
                    if '<meta itemprop="latitude" content="' in line:
                        lat = line.split('<meta itemprop="latitude" content="')[
                            1
                        ].split('"')[0]
                        lng = line.split('<meta itemprop="longitude" content="')[
                            1
                        ].split('"')[0]
                    if '"normalHours":[' in line:
                        days = (
                            line.split('"normalHours":[')[1]
                            .split(']},"')[0]
                            .split('"day":"')
                        )
                        for day in days:
                            if '"isClosed":' in day:
                                if '"isClosed":true' in day:
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
                if state == "":
                    state = "PR"
                if state == "PR":
                    country = "US"
                name = "Advance Auto Parts #" + store
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
                if tries <= 3:
                    LFound = True


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
