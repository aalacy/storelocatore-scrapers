from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("intercontinental_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.ihg.com/intercontinental/content/us/en/hotel-directory."
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a href="//www.ihg.com/intercontinental/hotels/us/en/' in line:
            lurl = "https:" + line.split('href="')[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl)
    for loc in locs:
        try:
            logger.info(loc)
            r2 = session.get(loc, headers=headers)
            website = "intercontinental.com"
            name = ""
            city = ""
            state = ""
            country = ""
            add = ""
            zc = ""
            typ = "Hotel"
            phone = ""
            hours = "<MISSING>"
            lat = ""
            lng = ""
            add2 = ""
            city2 = ""
            zc2 = ""
            state2 = ""
            phone2 = ""
            country2 = ""
            lat2 = ""
            lng2 = ""
            store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
            for line2 in r2.iter_lines():
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                if 'property="og:title" content="' in line2 and name == "":
                    name = line2.split('property="og:title" content="')[1].split('"')[0]
                if '"name" : "' in line2 and name == "":
                    name = line2.split('"name" : "')[1].split('"')[0]
                if '"streetAddress": "' in line2 and add == "":
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if '<span itemprop="streetAddress">' in line2 and add == "":
                    add = (
                        line2.split('<span itemprop="streetAddress">')[1]
                        .split("</span>")[0]
                        .strip()
                        .replace("<p>", "")
                        .replace("</p>", "")
                        .strip()
                    )
                    city = (
                        line2.split('<span itemprop="addressLocality">')[1]
                        .split("<")[0]
                        .strip()
                    )
                    try:
                        state = line2.split('<span itemprop="addressRegion">')[1].split(
                            "<"
                        )[0]
                    except:
                        state = "<MISSING>"
                    try:
                        zc = line2.split('<span itemprop="zipCode">')[1].split("<")[0]
                    except:
                        zc = "<MISSING>"
                    try:
                        country = line2.split('<span itemprop="addressCountry">')[
                            1
                        ].split("<")[0]
                    except:
                        country = "<MISSING>"
                if '"addressLocality": "' in line2 and city == "":
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                if lat == "" and '<meta itemprop="latitude" content="' in line2:
                    lat = line2.split('<meta itemprop="latitude" content="')[1].split(
                        '"'
                    )[0]
                if lng == "" and '<meta itemprop="longitude" content="' in line2:
                    lng = line2.split('<meta itemprop="longitude" content="')[1].split(
                        '"'
                    )[0]
                if '"addressRegion": "' in line2 and state == "":
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                if phone == "" and 'itemprop="telephone">' in line2:
                    phone = line2.split('<span itemprop="telephone">')[1].split(
                        "<span>"
                    )[0]
                    if "tel:" in phone:
                        phone = phone.split("tel:")[1].split('"')[0]
                if '"addressCountry": "' in line2 and country == "":
                    country = line2.split('"addressCountry": "')[1].split('"')[0]
                if '"latitude": "' in line2 and lat == "":
                    lat = line2.split('"latitude": "')[1].split('"')[0]
                if '"longitude": "' in line2 and lng == "":
                    lng = line2.split('"longitude": "')[1].split('"')[0]
                if '"telephone": "' in line2 and phone == "":
                    phone = line2.split('"telephone": "')[1].split('"')[0]
                if 'itemprop="streetAddress">' in line2:
                    add2 = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                if 'itemprop="addressRegion">' in line2:
                    state2 = line2.split('itemprop="addressRegion">')[1].split("<")[0]
                if 'itemprop="addressLocality">' in line2:
                    city2 = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                if 'itemprop="postalCode">' in line2:
                    zc2 = line2.split('itemprop="postalCode">')[1].split("<")[0]
                if '<meta itemprop="latitude" content="' in line2:
                    lat2 = line2.split('<meta itemprop="latitude" content="')[1].split(
                        '"'
                    )[0]
                if '<meta itemprop="longitude" content="' in line2:
                    lng2 = line2.split('<meta itemprop="longitude" content="')[1].split(
                        '"'
                    )[0]
                if 'itemprop="telephone">' in line2:
                    phone2 = line2.split('itemprop="telephone">')[1].split("<")[0]
                if 'itemprop="addressCountry">' in line2:
                    country2 = line2.split('itemprop="addressCountry">')[1].split("<")[
                        0
                    ]
            if add == "":
                add = add2
            if city == "":
                city = city2
            if state == "":
                state = state2
            if zc == "":
                zc = zc2
            if lat == "":
                lat = lat2
            if lng == "":
                lng = lng2
            if country == "":
                country = country2
            if phone == "":
                phone = phone2
            if "null" in phone or phone == "":
                phone = "<MISSING>"
            if state == "":
                state = "<MISSING>"
            if add == "":
                add = "<MISSING>"
            if lat == "":
                lat = "<MISSING>"
            if lng == "":
                lng = "<MISSING>"
            if zc == "":
                zc = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if city == "":
                city = "<MISSING>"
            if "/en/macao/" in loc:
                country = "China"
            state = state.replace("&nbsp;", "")
            city = city.replace("&nbsp;", "")
            if len(phone) <= 5:
                phone = "<MISSING>"
            if (
                "1" not in phone
                and "2" not in phone
                and "3" not in phone
                and "4" not in phone
                and "5" not in phone
                and "6" not in phone
                and "7" not in phone
            ):
                phone = "<MISSING>"
            city = city.replace("&#39;", "'")
            add = add.replace("&#39;", "'")
            if " Hotels" not in name and name != "":
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
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
