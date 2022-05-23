from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bigy_com")


def fetch_data():
    for x in range(1, 130):
        url = "https://www.bigy.com/rs/storelocator/detail/" + str(x)
        r = session.get(url, headers=headers)
        website = "bigy.com"
        typ = "<MISSING>"
        country = "US"
        loc = url
        store = str(x)
        name = ""
        logger.info("Pulling Store #%s..." % str(x))
        lines = r.iter_lines()
        for line in lines:
            if '<h1 class="txt-find-a-store">' in line:
                name = (
                    line.split('<h1 class="txt-find-a-store">')[1].split("<")[0].strip()
                )
            if '"Address1":"' in line:
                add = line.split('"Address1":"')[1].split('"')[0]
                city = line.split('"City":"')[1].split('"')[0]
                state = line.split('"State":"')[1].split('"')[0]
                zc = line.split('"Zipcode":"')[1].split('"')[0]
                phone = line.split('"PhoneNumber":"')[1].split('"')[0]
            if ">Hours:</span>" in line:
                hours = line.split(">Hours:</span>")[1].split("<")[0].strip()
            if '"Latitude":' in line:
                lat = line.split('"Latitude":')[1].split(",")[0]
                lng = line.split('"Longitude":')[1].split(",")[0]
        if name != "":
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
