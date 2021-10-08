from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "path": "/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?postalCode=90210&countryCode=US&distanceUnit=imperial&maxdistance=5&carters=false&oshkosh=false&skiphop=true&retail=true&wholesale=true&lat=34.0679551&lng=-118.4011509",
    "method": "GET",
    "authority": "www.skiphop.com",
}


def fetch_data():
    url = "https://www.skiphop.com/on/demandware.store/Sites-Carters-Site/default/Stores-GetNearestStores?postalCode=90210&countryCode=US&distanceUnit=imperial&maxdistance=5000&carters=false&oshkosh=false&skiphop=true&retail=true&wholesale=true&lat=40.0&lng=-95.0"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "skiphop.com"
    country = "US"
    loc = "<MISSING>"
    for line in r.iter_lines(decode_unicode=True):
        if '"name": "' in line:
            name = line.split('"name": "')[1].split('"')[0]
        if '"brand": "' in line:
            typ = line.split('"brand": "')[1].split('"')[0]
        if '"storeid": "' in line:
            store = line.split('"storeid": "')[1].split('"')[0]
        if '"address1": "' in line:
            add = line.split('"address1": "')[1].split('"')[0]
        if '"address2": "' in line:
            line.split('"address2": "')[1].split('"')[0]
            add = add.strip()
        if '"city": "' in line:
            city = line.split('"city": "')[1].split('"')[0]
        if '"stateCode": "' in line:
            state = line.split('"stateCode": "')[1].split('"')[0]
        if '"postalCode": "' in line:
            zc = line.split('"postalCode": "')[1].split('"')[0]
        if '"phone": "' in line:
            phone = line.split('"phone": "')[1].split('"')[0]
        if '"latitude": ' in line:
            lat = line.split('"latitude": ')[1].split(",")[0]
        if '"longitude": ' in line:
            lng = line.split('"longitude": ')[1].split(",")[0]
            loc = "<MISSING>"
        if '"sundayHours": ""' in line:
            hours = "<MISSING>"
        if '"sundayHours": "' in line and '"sundayHours": ""' not in line:
            hours = "Sun: " + line.split('"sundayHours": "')[1].split('"')[0]
        if '"mondayHours"' in line and hours != "<MISSING>":
            hours = hours + "; Mon: " + line.split('"mondayHours": "')[1].split('"')[0]
        if '"tuesdayHours"' in line and hours != "<MISSING>":
            hours = hours + "; Tue: " + line.split('"tuesdayHours": "')[1].split('"')[0]
        if '"wednesdayHours"' in line and hours != "<MISSING>":
            hours = (
                hours + "; Wed: " + line.split('"wednesdayHours": "')[1].split('"')[0]
            )
        if '"thursdayHours"' in line and hours != "<MISSING>":
            hours = (
                hours + "; Thu: " + line.split('"thursdayHours": "')[1].split('"')[0]
            )
        if '"fridayHours"' in line and hours != "<MISSING>":
            hours = hours + "; Fri: " + line.split('"fridayHours": "')[1].split('"')[0]
        if '"saturdayHours"' in line and hours != "<MISSING>":
            hours = (
                hours + "; Sat: " + line.split('"saturdayHours": "')[1].split('"')[0]
            )
        if '"saturdayHours"' in line:
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if lat == "" or lng == "":
                lat = "<MISSING>"
                lng = "<MISSING>"
            if add == "":
                add = "<MISSING>"
            if state == "SL":
                state = "FL"
            if city == "Ca":
                city = state
                state = "CA"
            if state == "NEW JERSEY":
                state = "NJ"
            if state == "CALIFORNIA":
                state = "CA"
            if state == "MISSISSIPPI":
                state = "MS"
            if state == "ONTARIO":
                state = "ON"
            if city == "St. Paul":
                state = "MN"
            if city == "San Diego":
                state = "CA"
            if state == "BC" or state == "ON" or state == "QC":
                country = "CA"
            if state.lower() == "virginia":
                state = "VA"
            if city == "35":
                city = "California"
            if "," in name:
                name = name.split(",")[0]
            if "CLOSED-CLOSED" in hours:
                hours = "TEMPORARILY CLOSED"
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
