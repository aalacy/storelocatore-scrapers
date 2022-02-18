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

logger = SgLogSetup().get_logger("dominospizza_pl")


def fetch_data():
    locs = []
    url = "https://dominospizza.pl/lokale"
    r = session.get(url, headers=headers)
    website = "dominospizza.pl"
    typ = "<MISSING>"
    country = "PL"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if (
            '<h5 class="PlaceInfo__street"><a href="https://www.dominospizza.pl/Lokale/'
            in line
        ):
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        state = "<MISSING>"
        add = ""
        city = ""
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        store = ""
        HFound = False
        zc = "<MISSING>"
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if '="PlaceInfo__street">' in line2 and add == "":
                add = line2.split('="PlaceInfo__street">')[1].split("<")[0]
            if '"PlaceInfo__city">' in line2 and city == "":
                city = line2.split('"PlaceInfo__city">')[1].split("<")[0]
            if phone == "" and 'class="PlaceInfo__phone">' in line2:
                phone = line2.split("tel:")[1].split('"')[0]
            if 'rc="https://maps.googleapis.com/maps/api/staticmap?center=' in line2:
                lat = line2.split(
                    'rc="https://maps.googleapis.com/maps/api/staticmap?center='
                )[1].split(",")[0]
                lng = (
                    line2.split(
                        'rc="https://maps.googleapis.com/maps/api/staticmap?center='
                    )[1]
                    .split(",")[1]
                    .split("&")[0]
                )
            if "Godziny otwarcia" in line2 and hours == "":
                HFound = True
            if HFound and '<div class="m-OpeningHours' in line2:
                HFound = False
            if HFound and "<span>" in line2 and "> - <" not in line2:
                day = line2.split("<span>")[1].split("<")[0]
            if HFound and "</span> - <span>" in line2:
                hrs = (
                    day
                    + ": "
                    + line2.replace("</span> - <span>", "-").split(">")[1].split("<")[0]
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
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
