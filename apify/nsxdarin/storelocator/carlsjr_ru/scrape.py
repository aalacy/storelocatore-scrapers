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

logger = SgLogSetup().get_logger("carlsjr_ru")


def fetch_data():
    urls = [
        "http://carlsjr.ru/adresa/spb/",
        "http://carlsjr.ru/adresa/msk/",
        "http://carlsjr.ru/adresa/novosibirsk/",
        "http://carlsjr.ru/adresa/norilsk/",
        "http://carlsjr.ru/adresa/chita/",
    ]
    for url in urls:
        logger.info(url)
        coords = []
        r = session.get(url, headers=headers)
        website = "carlsjr.ru"
        typ = "<MISSING>"
        country = "RU"
        phone = "<MISSING>"
        lines = r.iter_lines()
        for line in lines:
            if "myGeoObjects.add(new ymaps.Placemark([" in line:
                clat = line.split("myGeoObjects.add(new ymaps.Placemark([")[1].split(
                    ","
                )[0]
                clng = (
                    line.split("myGeoObjects.add(new ymaps.Placemark([")[1]
                    .split(",")[1]
                    .split("]")[0]
                )
            if 'balloonContentFooter: "' in line:
                cid = line.split("href='")[1].split("/'")[0].rsplit("/", 1)[1]
                coords.append(cid + "|" + clat + "|" + clng)
            if '<div class="adressDiv"' in line:
                city = line.split('data-metro="')[1].split('"')[0]
                state = line.split('data-region="')[1].split('"')[0]
                g = next(lines)
                store = g.split('href="')[1].split('/"')[0].rsplit("/", 1)[1]
                loc = "http://carlsjr.ru" + g.split('href="')[1].split('"')[0]
                name = g.split('">')[1].split("<")[0].strip()
                g = next(lines)
                zc = "<MISSING>"
                add = g.split("<br/>")[1].split("<")[0].strip()
                hours = g.rsplit("<br/>", 1)[1].split("<")[0].strip().replace("\t", "")
                lat = "<MISSING>"
                lng = "<MISSING>"
                for coord in coords:
                    if store == coord.split("|")[0]:
                        lat = coord.split("|")[1]
                        lng = coord.split("|")[2]
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
