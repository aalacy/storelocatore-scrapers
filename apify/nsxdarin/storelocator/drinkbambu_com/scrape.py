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
    canada = ["AB", "BC", "ON", "QC", "PEI", "SK", "NB", "NL", "NS", "PE"]
    url = "https://www.drinkbambu.com/find-bambu/"
    r = session.get(url, headers=headers)
    website = "drinkbambu.com"
    country = "US"
    for line in r.iter_lines():
        if "<a class='view-loc' href='" in line:
            items = line.split("<a class='view-loc' href='")
            for item in items:
                if ">View Location</a>" in item:
                    locs.append("https://www.drinkbambu.com" + item.split("'")[0])
    for loc in locs:
        CS = False
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        typ = "<MISSING>"
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "Coming Soon" in line2:
                CS = True
            if '<h1 itemprop="name">' in line2:
                name = line2.split('<h1 itemprop="name">')[1].split("<")[0]
            if '<span itemprop="address">' in line2:
                add = (
                    line2.split('<span itemprop="address">')[1]
                    .split('<span itemprop="addressLocality">')[0]
                    .replace("<br/>", "")
                    .replace("</span>", "")
                    .replace("<br />", "")
                    .strip()
                )
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if 'itemprop="telephone" content="' in line2:
                phone = (
                    line2.split('itemprop="telephone" content="')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
            if 'itemprop="openingHours">' in line2:
                hours = line2.split('itemprop="openingHours">')[1].split("<")[0]
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        hours = hours.replace("|", ";").replace("  ", " ")
        name = name.replace("&#8217;", "'")
        if state in canada:
            country = "CA"
        else:
            country = "US"
        if "<" in add:
            add = add.split("<")[0]
        add = add.strip()
        if "Regular Hours" in hours:
            hours = hours.split("Regular Hours")[1].strip()
        name = name.replace("&#8211;", "-")
        if " " in zc:
            country = "CA"
        if city != "" and CS is False:
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
