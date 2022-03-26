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
    locs = []
    states = []
    cities = []
    url = "https://locations.marazziusa.com/"
    r = session.get(url, headers=headers)
    website = "marazzitile.com"
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'data-galoc="State Index page' in line:
            lurl = line.split('href="')[1].split('"')[0]
            states.append(lurl)
    for state in states:
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'data-galoc="City Level' in line2:
                cities.append(line2.split('href="')[1].split('"')[0])
    for city in cities:
        r2 = session.get(city, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if 'data-gaact="Click_to_ViewLocalPage"' in line2:
                locs.append(line2.split('href="')[1].split('/"')[0])
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        country = "US"
        phone = ""
        store = loc.rsplit("/", 1)[1]
        typ = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if 'property="og:title" content="' in line2:
                name = line2.split('property="og:title" content="')[1].split('"')[0]
            if 'property="business:contact_data:street_address" content="' in line2:
                add = line2.split(
                    'property="business:contact_data:street_address" content="'
                )[1].split('"')[0]
            if 'property="business:contact_data:locality" content="' in line2:
                city = line2.split(
                    'property="business:contact_data:locality" content="'
                )[1].split('"')[0]
            if 'property="business:contact_data:region" content="' in line2:
                state = line2.split(
                    'property="business:contact_data:region" content="'
                )[1].split('"')[0]
            if 'property="business:contact_data:postal_code" content="' in line2:
                zc = line2.split(
                    'property="business:contact_data:postal_code" content="'
                )[1].split('"')[0]
            if 'property="business:contact_data:phone_number" content="' in line2:
                phone = line2.split(
                    'property="business:contact_data:phone_number" content="'
                )[1].split('"')[0]
            if 'place:location:latitude" content="' in line2:
                lat = line2.split('place:location:latitude" content="')[1].split('"')[0]
            if 'place:location:longitude" content="' in line2:
                lng = line2.split('place:location:longitude" content="')[1].split('"')[
                    0
                ]
            if "</style>" in line2:
                g = next(lines)
                g = str(g.decode("utf-8"))
                if "<h3>" in g:
                    typ = g.split(">")[1].split("<")[0]
            if "var hoursArray" in line2:
                days = line2.split("Array('")
                for day in days:
                    if "')," in day:
                        hrs = (
                            day.split("'")[0]
                            + ": "
                            + day.split(", '")[1].split("'")[0]
                            + "-"
                            + day.split(", '")[2].split("'")[0]
                        )
                        hrs = hrs.replace("CLOSED-CLOSED", "Closed")
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
        if hours == "" or "AM" not in hours:
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if city != "":
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
