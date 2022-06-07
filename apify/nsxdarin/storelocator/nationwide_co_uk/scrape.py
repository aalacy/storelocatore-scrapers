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

logger = SgLogSetup().get_logger("nationwide_co_uk")


def fetch_data():
    locs = []
    cities = []
    url = "https://www.nationwide.co.uk/branches/index.html"
    r = session.get(url, headers=headers)
    website = "nationwide.co.uk"
    typ = "<MISSING>"
    country = "GB"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '<a class="Directory-listLink" href="' in line:
            items = line.split('<a class="Directory-listLink" href="')
            for item in items:
                if "<!doctype html>" not in item:
                    lurl = "https://www.nationwide.co.uk/branches/" + item.split('"')[0]
                    if 'data-count="(' in item:
                        cities.append(lurl.replace("&#39;", "'").replace("&amp;", "&"))
                    else:
                        locs.append(lurl.replace("&#39;", "'").replace("&amp;", "&"))
    for curl in cities:
        logger.info(curl)
        r = session.get(curl, headers=headers)
        for line in r.iter_lines():
            if 'Teaser-title Link--extraLarge" href="' in line:
                items = line.split('Teaser-title Link--extraLarge" href="')
                for item in items:
                    if 'data-ya-track="businessname' in item:
                        lurl = (
                            "https://www.nationwide.co.uk/branches/"
                            + item.split('"')[0]
                        )
                        locs.append(lurl.replace("&#39;", "'").replace("&amp;", "&"))
    for loc in locs:
        Closed = False
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "permanently closed" in line2.lower():
                Closed = True
            if "details_name']= \"" in line2:
                name = line2.split("details_name']= \"")[1].split('"')[0]
            if add == "" and 'class="c-address-street-1">' in line2:
                add = line2.split('class="c-address-street-1">')[1].split("<")[0]
                city = line2.split('class="c-address-city">')[1].split("<")[0]
                state = "<MISSING>"
                try:
                    zc = line2.split('itemprop="postalCode">')[1].split("<")[0]
                except:
                    zc = "<MISSING>"
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'c-phone-main-number-link" href="tel:' in line2 and phone == "":
                phone = line2.split('c-phone-main-number-link" href="tel:')[1].split(
                    '"'
                )[0]
            if "data-days='[{" in line2 and hours == "":
                days = line2.split("data-days='[{")[1].split("}]'")[0].split('"day":"')
                for day in days:
                    if '"intervals":' in day:
                        hrs = day.split('"')[0] + ": "
                        if '"intervals":[]' in day:
                            hrs = hrs + "Closed"
                        else:
                            hrs = (
                                hrs
                                + day.split('"start":')[1].split("}")[0]
                                + "-"
                                + day.split('"end":')[1].split(",")[0]
                            )
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if phone == "":
            phone = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
            lng = "<MISSING>"
        if Closed is False:
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
