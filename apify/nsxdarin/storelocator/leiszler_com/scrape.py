from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    coords = []
    places = []
    url = "https://www.leiszler.com/locations/"
    r = session.get(url, headers=headers)
    lines = r.iter_lines()
    for line in lines:
        if "new google.maps.LatLng(" in line:
            latlng = (
                line.split("new google.maps.LatLng(")[1].split(",")[0]
                + "|"
                + line.split(", ")[1].split(")")[0]
            )
        if '<div class="title">' in line:
            title = line.split('"title">')[1].split("<")[0].replace("&#039;", "'")
            coords.append(title + "|" + latlng)
        if (
            'class="img-responsive" /><a href="https://www.leiszler.com/locations/location/'
            in line
        ):
            items = line.split('class="img-responsive" /><a href="')
            for item in items:
                if '<div class="row location-rows">' not in item:
                    loc = item.split('"')[0]
                    name = item.split('<span itemprop="name">')[1].split("<")[0]
                    try:
                        phone = item.split('itemprop="telephone">')[1].split("<")[0]
                    except:
                        phone = "<MISSING>"
                    hours = "<MISSING>"
                    website = "leiszler.com"
                    add = item.split('"streetAddress">')[1].split("<")[0]
                    city = item.split('"addressLocality">')[1].split("<")[0]
                    zc = item.split('"postalCode">')[1].split("<")[0]
                    state = item.split('"addressRegion">')[1].split("<")[0]
                    country = "US"
                    store = "<MISSING>"
                    typ = "Store"
                    hours = "<MISSING>"
                    info = (
                        website
                        + "|"
                        + loc
                        + "|"
                        + name
                        + "|"
                        + add
                        + "|"
                        + city
                        + "|"
                        + state
                        + "|"
                        + zc
                        + "|"
                        + country
                        + "|"
                        + store
                        + "|"
                        + phone
                        + "|"
                        + typ
                        + "|"
                        + hours
                    )
                    places.append(info)
    for item in coords:
        for place in places:
            if place.split("|")[2] == item.split("|")[0]:
                lat = item.split("|")[1]
                lng = item.split("|")[2]
                website = place.split("|")[0]
                loc = place.split("|")[1]
                name = place.split("|")[2]
                add = place.split("|")[3]
                city = place.split("|")[4]
                state = place.split("|")[5]
                zc = place.split("|")[6]
                country = place.split("|")[7]
                store = place.split("|")[8]
                phone = place.split("|")[9]
                typ = place.split("|")[10]
                hours = place.split("|")[11]
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
