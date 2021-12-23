from sgrequests import SgRequests
from tenacity import retry, stop_after_attempt
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


@retry(stop=stop_after_attempt(7))
def get(loc):
    session = SgRequests()
    return session.get(loc, headers=headers)


def fetch_data():
    alllocs = []
    states = []
    url = "https://www.enterprise.com/en/car-rental/locations/us.html"
    r = get(url)
    for line in r.iter_lines():
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = "https://www.enterprise.com" + line.split('href="')[1].split('"')[0]
            states.append(lurl + "|US")
    url = "https://www.enterprise.com/en/car-rental/locations/canada.html"
    r = get(url)
    for line in r.iter_lines():
        if '<h3 class="state-title"><a class="heading-link" href="' in line:
            lurl = "https://www.enterprise.com" + line.split('href="')[1].split('"')[0]
            states.append(lurl + "|CA")
    for state in states:
        surl = state.split("|")[0]
        country = state.split("|")[1]
        locs = []
        r2 = get(surl)
        for line2 in r2.iter_lines():
            if '<a href="https://www.enterprise.com/en/car-rental/locations/' in line2:
                lurl = line2.split('href="')[1].split('"')[0]
                if lurl not in alllocs:
                    alllocs.append(lurl)
                    locs.append(lurl)
        for loc in locs:
            website = "enterprise.com"
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = ""
            phone = ""
            typ = "<MISSING>"
            lat = ""
            lng = ""
            hours = ""
            r3 = get(loc)
            for line3 in r3.iter_lines():
                if 'enterprise.locationDetail.locationmap.locationId = "' in line3:
                    store = line3.split(
                        'enterprise.locationDetail.locationmap.locationId = "'
                    )[1].split('"')[0]
                    surl = (
                        "https://prd-west.webapi.enterprise.com/enterprise-ewt/location/"
                        + store
                    )
                    try:
                        r4 = get(surl)
                        for line4 in r4.iter_lines():
                            if '"hours":[{"type":"STANDARD","days":[{' in line4:
                                days = (
                                    line4.split(
                                        '"hours":[{"type":"STANDARD","days":[{'
                                    )[1]
                                    .split("]}]},")[0]
                                    .split('"day":"')
                                )
                                for day in days:
                                    if '"date":"' in day:
                                        if '"closed_all_day":true' in day:
                                            hrs = day.split('"')[0] + ": Closed"
                                        else:
                                            hrs = (
                                                day.split('"')[0]
                                                + ": "
                                                + day.split('{"open_time":"')[1].split(
                                                    '"'
                                                )[0]
                                                + "-"
                                                + day.split('"close_time":"')[1].split(
                                                    '"'
                                                )[0]
                                            )
                                        if hours == "":
                                            hours = hrs
                                        else:
                                            hours = hours + "; " + hrs
                    except:
                        hours = "<MISSING>"
                if '"locationName": "' in line3:
                    name = line3.split('"locationName": "')[1].split('"')[0]
                if '"streetAddress" : "' in line3:
                    add = line3.split('"streetAddress" : "')[1].split('"')[0]
                if '"addressLocality" : "' in line3:
                    city = line3.split('"addressLocality" : "')[1].split('"')[0]
                if '"addressRegion" : "' in line3:
                    state = line3.split('"addressRegion" : "')[1].split('"')[0]
                if '"postalCode" : "' in line3:
                    zc = line3.split('"postalCode" : "')[1].split('"')[0]
                if '"telephone" : "' in line3:
                    phone = (
                        line3.split('"telephone" : "')[1].split('"')[0].replace("+", "")
                    )
                if '"latitude" : "' in line3:
                    lat = line3.split('"latitude" : "')[1].split('"')[0]
                if '"longitude" : "' in line3:
                    lng = line3.split('longitude" : "')[1].split('"')[0]
            if hours == "":
                hours = "<MISSING>"
            name = name.replace("&amp;", "&").replace("&#39;", "'")
            if store == "":
                store = "<MISSING>"
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
