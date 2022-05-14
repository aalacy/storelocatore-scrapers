from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("bgca_org")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    for x in range(50, 70, 2):
        for y in range(-170, -120, 2):
            lat = str(x)
            lng = str(y)
            logger.info((str(lat) + "," + str(lng)))
            url = (
                "https://bgcaorg-find-a-c-1488560011850.appspot.com//x/v1/clubs/"
                + lat
                + "/"
                + lng
                + "/500/"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"City": "' in line:
                    typ = "<MISSING>"
                    loc = "<MISSING>"
                    hours = "<MISSING>"
                    country = ""
                    website = "bgca.org"
                    city = line.split('"City": "')[1].split('"')[0]
                if '"ZipCode1": "' in line:
                    zc = line.split('"ZipCode1": "')[1].split('"')[0]
                if '"State": "' in line:
                    state = line.split('"State": "')[1].split('"')[0]
                if '"Country": "USA"' in line:
                    country = "US"
                if '"PhoneNumber": "' in line:
                    phone = line.split('"PhoneNumber": "')[1].split('"')[0]
                if '"lng": ' in line:
                    lng = line.split('"lng": ')[1].split(",")[0]
                if '"lat": ' in line:
                    lat = line.split('"lat": ')[1].split(",")[0]
                if '"Address1": "' in line:
                    add = line.split('"Address1": "')[1].split('"')[0]
                if '"Address2": "' in line:
                    add = add + " " + line.split('"Address2": "')[1].split('"')[0]
                if '"SiteId": "' in line:
                    store = line.split('"SiteId": "')[1].split('"')[0]
                if '"SiteName": "' in line:
                    name = line.split('"SiteName": "')[1].split('"')[0]
                if '"Native": "' in line:
                    if country == "US":
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
    for x in range(10, 20, 2):
        for y in range(-160, -140, 2):
            lat = str(x)
            lng = str(y)
            logger.info((str(lat) + "," + str(lng)))
            url = (
                "https://bgcaorg-find-a-c-1488560011850.appspot.com//x/v1/clubs/"
                + lat
                + "/"
                + lng
                + "/500/"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"City": "' in line:
                    typ = "<MISSING>"
                    loc = "<MISSING>"
                    hours = "<MISSING>"
                    country = ""
                    website = "bgca.org"
                    city = line.split('"City": "')[1].split('"')[0]
                if '"ZipCode1": "' in line:
                    zc = line.split('"ZipCode1": "')[1].split('"')[0]
                if '"State": "' in line:
                    state = line.split('"State": "')[1].split('"')[0]
                if '"Country": "USA"' in line:
                    country = "US"
                if '"PhoneNumber": "' in line:
                    phone = line.split('"PhoneNumber": "')[1].split('"')[0]
                if '"lng": ' in line:
                    lng = line.split('"lng": ')[1].split(",")[0]
                if '"lat": ' in line:
                    lat = line.split('"lat": ')[1].split(",")[0]
                if '"Address1": "' in line:
                    add = line.split('"Address1": "')[1].split('"')[0]
                if '"Address2": "' in line:
                    add = add + " " + line.split('"Address2": "')[1].split('"')[0]
                if '"SiteId": "' in line:
                    store = line.split('"SiteId": "')[1].split('"')[0]
                if '"SiteName": "' in line:
                    name = line.split('"SiteName": "')[1].split('"')[0]
                if '"Native": "' in line:
                    if country == "US":
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

    for x in range(24, 50):
        for y in range(-126, -66):
            lat = str(x)
            lng = str(y)
            logger.info((str(lat) + "," + str(lng)))
            url = (
                "https://bgcaorg-find-a-c-1488560011850.appspot.com//x/v1/clubs/"
                + lat
                + "/"
                + lng
                + "/250/"
            )
            r = session.get(url, headers=headers)
            for line in r.iter_lines():
                if '"City": "' in line:
                    typ = "<MISSING>"
                    loc = "<MISSING>"
                    hours = "<MISSING>"
                    country = ""
                    website = "bgca.org"
                    city = line.split('"City": "')[1].split('"')[0]
                if '"ZipCode1": "' in line:
                    zc = line.split('"ZipCode1": "')[1].split('"')[0]
                if '"State": "' in line:
                    state = line.split('"State": "')[1].split('"')[0]
                if '"Country": "USA"' in line:
                    country = "US"
                if '"PhoneNumber": "' in line:
                    phone = line.split('"PhoneNumber": "')[1].split('"')[0]
                if '"lng": ' in line:
                    lng = line.split('"lng": ')[1].split(",")[0]
                if '"lat": ' in line:
                    lat = line.split('"lat": ')[1].split(",")[0]
                if '"Address1": "' in line:
                    add = line.split('"Address1": "')[1].split('"')[0]
                if '"Address2": "' in line:
                    add = add + " " + line.split('"Address2": "')[1].split('"')[0]
                if '"SiteId": "' in line:
                    store = line.split('"SiteId": "')[1].split('"')[0]
                if '"SiteName": "' in line:
                    name = line.split('"SiteName": "')[1].split('"')[0]
                if '"Native": "' in line:
                    if country == "US":
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
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
