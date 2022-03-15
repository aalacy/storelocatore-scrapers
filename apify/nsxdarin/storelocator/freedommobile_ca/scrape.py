from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "authorization": "Bearer W-MoWHdA6mZ7feLxKiOTWXz9qd4eRDNHIhHfjbKZRgQ",
}

logger = SgLogSetup().get_logger("freedommobile_ca")


def fetch_data():
    addarray = []
    dayarray = []
    stores = []
    urls = [
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-75%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-85%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-95%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-105%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-115%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=50%2C-125%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=45%2C-70%2C1000",
        "https://cdn.contentful.com/spaces/521j506nwxqw/environments/master/entries?locale=en-US&include=5&limit=1000&content_type=store&fields.onTheMap%5Bwithin%5D=45%2C-80%2C1000",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "freedommobile.ca"
        typ = "<MISSING>"
        country = "CA"
        logger.info("Pulling Stores")
        allinfo = str(r.content.decode("utf-8"))
        allinfo = allinfo.replace("\r", "").replace("\n", "")
        dayinfo = allinfo.replace('"id": "master",', "").replace(
            '"id": "storeHours"', "STOREHOURS"
        )
        addinfo = allinfo.replace('"id": "master",', "").replace(
            '"id": "address"', "ADDRESSINFO"
        )
        days = dayinfo.split('"id": "')
        for day in days:
            if "STOREHOURS" in day:
                did = day.split('"')[0]
                dhrs = day.split('"hours": "')[1].split('"')[0]
                dayarray.append(did + "|" + dhrs)
        adds = addinfo.split('"id": "')
        for additem in adds:
            if "ADDRESSINFO" in additem:
                aid = additem.split('"')[0]
                a1 = (
                    additem.split('"streetNumber": "')[1].split('"')[0]
                    + " "
                    + additem.split('"streetName": "')[1].split('"')[0]
                )
                a2 = additem.split('"city": "')[1].split('"')[0]
                a3 = additem.split('"province": "')[1].split('"')[0]
                a4 = additem.split('"postalCode": "')[1].split('"')[0]
                try:
                    a5 = additem.split('"nearestIntersection": "')[1].split('"')[0]
                except:
                    a5 = ""
                addarray.append(
                    aid + "|" + a1 + "|" + a2 + "|" + a3 + "|" + a4 + "|" + a5
                )
        items = allinfo.split('"locationNumber": "')
        for item in items:
            if '"total":' not in item:
                store = item.split('"')[0]
                lurl = "https://locations.freedommobile.ca/store/" + store
                name = item.split('"name": "')[1].split('"')[0]
                phone = item.split('"phone": "')[1].split('"')[0]
                try:
                    aid = (
                        item.split('"address": {')[1].split('"id": "')[1].split('"')[0]
                    )
                except:
                    aid = "<MISSING>"
                try:
                    mhrs = item.split('"Monday":')[1].split('"id": "')[1].split('"')[0]
                except:
                    mhrs = ""
                try:
                    thrs = item.split('"Tuesday":')[1].split('"id": "')[1].split('"')[0]
                except:
                    thrs = ""
                try:
                    whrs = (
                        item.split('"Wednesday":')[1].split('"id": "')[1].split('"')[0]
                    )
                except:
                    whrs = ""
                try:
                    thhrs = (
                        item.split('"Thursday":')[1].split('"id": "')[1].split('"')[0]
                    )
                except:
                    thhrs = ""
                try:
                    fhrs = item.split('"Friday":')[1].split('"id": "')[1].split('"')[0]
                except:
                    fhrs = ""
                try:
                    shrs = (
                        item.split('"Saturday":')[1].split('"id": "')[1].split('"')[0]
                    )
                except:
                    shrs = ""
                try:
                    suhrs = item.split('"Sunday":')[1].split('"id": "')[1].split('"')[0]
                except:
                    suhrs = ""
                lat = item.split('"lat": ')[1]
                if '"lon": ' in lat:
                    lat = lat.split(",")[0]
                else:
                    lat = lat.split("}")[0].strip()
                lng = item.split('"lon": ')[1]
                if '"lat": ' in lng:
                    lng = lng.split(",")[0]
                else:
                    lng = lng.split("}")[0].strip()
                add = ""
                city = ""
                state = ""
                zc = ""
                for aitem in addarray:
                    if aitem.split("|")[0] == aid:
                        add = aitem.split("|")[1]
                        city = aitem.split("|")[2]
                        state = aitem.split("|")[3]
                        zc = aitem.split("|")[4]
                        ni = aitem.split("|")[5]
                        if ni != "":
                            name = name + " - " + ni
                for hitem in dayarray:
                    if hitem.split("|")[0] == suhrs:
                        h1 = "Sunday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == mhrs:
                        h2 = "Monday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == thrs:
                        h3 = "Tuesday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == whrs:
                        h4 = "Wednesday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == thhrs:
                        h5 = "Thursday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == fhrs:
                        h6 = "Friday: " + hitem.split("|")[1]
                    if hitem.split("|")[0] == shrs:
                        h7 = "Saturday: " + hitem.split("|")[1]
                hours = (
                    h1
                    + "; "
                    + h2
                    + "; "
                    + h3
                    + "; "
                    + h4
                    + "; "
                    + h5
                    + "; "
                    + h6
                    + "; "
                    + h7
                )
                if store not in stores:
                    stores.append(store)
                    purl = ""
                    if "/wd" in lurl or "/WD" in lurl or "/wc" in lurl or "/WC" in lurl:
                        purl = lurl
                    else:
                        purl = "<MISSING>"
                    zc = zc[:3] + " " + zc[3:]
                    if add != "":
                        yield SgRecord(
                            locator_domain=website,
                            page_url=purl,
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
