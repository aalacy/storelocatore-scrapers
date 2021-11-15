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
    url = "https://www.ihg.com/intercontinental/content/us/en/explore"
    r = session.get(url, headers=headers)
    Found = False
    for line in r.iter_lines():
        if '"country-name">Canada' in line or '"country-name">United States' in line:
            Found = True
        if Found and '<a href="' in line:
            locs.append("https:" + line.split('href="')[1].split('"')[0])
        if Found and "</ul>" in line:
            Found = False
    for loc in locs:
        logger.info(("Pulling Hotel %s..." % loc))
        r2 = session.get(loc, headers=headers)
        website = "intercontinental.com"
        country = "US"
        typ = "Hotel"
        hours = "<MISSING>"
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        for line2 in r2.iter_lines():
            if 'itemprop="streetAddress">' in line2:
                add = line2.split('itemprop="streetAddress">')[1].split("<")[0]
                if 'itemprop="addressCountry">Canada' in line2:
                    country = "CA"
                city = line2.split('itemprop="addressLocality">')[1].split("<")[0]
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
                if zc == "":
                    zc = line2.split('itemprop="zipCode">')[1].split("<")[0]
            if '"postalCode": "' in line2:
                zc = line2.split('"postalCode": "')[1].split('"')[0]
            if 'itemprop="telephone"><a href="tel:+' in line2:
                phone = line2.split('itemprop="telephone"><a href="tel:+')[1].split(
                    '"'
                )[0]
            if 'itemprop="latitude" content="' in line2:
                lat = line2.split('itemprop="latitude" content="')[1].split('"')[0]
            if 'itemprop="longitude" content="' in line2:
                lng = line2.split('itemprop="longitude" content="')[1].split('"')[0]
            if 'property="og:url"' in line2:
                store = line2.split("/hoteldetail")[0].rsplit("/", 1)[1]
            if 'property="og:title" content="' in line2 and name == "":
                name = line2.split('property="og:title" content="')[1].split('"')[0]
        if phone == "":
            phone = "<MISSING>"
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
