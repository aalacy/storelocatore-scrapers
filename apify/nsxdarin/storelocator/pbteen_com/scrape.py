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
    url = "https://www.pbteen.com/customer-service/store-locator.html"
    r = session.get(url, headers=headers)
    website = "pbteen.com"
    typ = "Pottery Barn Teen"
    store = "<MISSING>"
    for line in r.iter_lines():
        if '<a href="https://www.pbteen.com/stores/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in locs:
                locs.append(lurl)
        if "<h3>Mexico City</h3>" in line:
            city = "Mexico City"
            country = "MX"
            state = "Hidalgo, Mexico D.F."
            name = "Pottery Barn Teen Polanco"
            add = "Torcuato Tasso 309, Col. Chapultepec Morales, Miguel"
            zc = "11570"
            phone = "11.03.77.15"
            lat = "19.4326258"
            lng = "-99.1840348"
            hours = "Sun-Sat: 11AM - 9PM"
            loc = "<MISSING>"
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
        if "<h3>Kuwait</h3>" in line:
            city = "Kuwait"
            country = "KW"
            state = "<MISSING>"
            lat = "29.3024914"
            lng = "47.9338832"
            phone = "+965 22283494"
            loc = "<MISSING>"
            name = "The Avenues, Phase 1, Al Rai"
            add = "The Avenues, Phase 1, Al Rai"
            hours = "Sun-Wed: 10AM - 10PM; Thur-Sat: 10AM - MIDNIGHT"
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
        if "<h3>United Arab Emirates</h3>" in line:
            city = "Abu Dhabi"
            country = "AE"
            state = "<MISSING>"
            lat = "24.4888196"
            lng = "54.6065011"
            loc = "<MISSING>"
            name = "Yas Mall, First Floor"
            add = "Yas Mall, First Floor"
            phone = "+971 800 803"
            hours = "Sun-Thur: 10AM - 10PM; Fri-Sat: 10AM - 11PM"
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
    for loc in locs:
        country = "US"
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if '<h3 class="store-name">' in line:
                name = line.split('<h3 class="store-name">')[1].split("<")[0]
            if '"latitude":' in line:
                lat = line.split('"latitude":')[1].split(",")[0]
                lng = line.split('"longitude":')[1].split(",")[0]
            if '<p class="store-address1">' in line:
                add = line.split('<p class="store-address1">')[1].split("<")[0]
            if '"addrLine1":"' in line:
                city = line.rsplit('"city":"', 1)[1].split('"')[0]
                state = line.rsplit('"stateProvince":"', 1)[1].split('"')[0]
                zc = line.rsplit('"postalCode":"', 1)[1].split('"')[0]
            if '<span class="store-address-phone">' in line:
                phone = line.split('<span class="store-address-phone">')[1].split("<")[
                    0
                ]
            if '"storeHoursMap":{' in line:
                hours = (
                    line.split('"storeHoursMap":{')[1]
                    .split("}")[0]
                    .replace('","', "; ")
                    .replace('"', "")
                )
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
