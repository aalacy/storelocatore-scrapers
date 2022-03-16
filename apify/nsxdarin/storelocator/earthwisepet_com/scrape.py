from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("earthwisepet_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    website = "earthwisepet.com"
    typ = "<MISSING>"
    store = "<MISSING>"
    hours = "<MISSING>"
    country = "US"
    for x in range(1, 21):
        logger.info(str(x))
        add = ""
        loc = ""
        name = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        lat = ""
        lng = ""
        url = "https://www.earthwisepet.com/stores/search/?page=" + str(x)
        r = session.get(url, headers=headers)
        lines = r.iter_lines()
        for line in lines:
            if '<i class="fa fa-phone"></i></span>' in line:
                g = next(lines)
                phone = g.strip().replace("\t", "").replace("\r", "").replace("\n", "")
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
            if '<h4 class="text-uppercase">' in line:
                g = next(lines)
                if 'href="/' not in g:
                    loc = g.split('href="')[1].split('"')[0]
                else:
                    loc = (
                        "https://earthwisepet.com" + g.split('href="')[1].split('"')[0]
                    )
                name = (
                    g.rsplit('">', 1)[1]
                    .split("<")[0]
                    .replace("&#39;", "'")
                    .replace("...", "")
                    .strip()
                )
            if ', US " tabindex="' in line:
                addinfo = line.split(', US " tabindex="')[0].split("q=")[1].strip()
                zc = addinfo.rsplit(",", 1)[1].strip()
                if addinfo.count(",") == 3:
                    add = addinfo.split(",")[0].strip()
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip()
                if addinfo.count(",") == 4:
                    add = (
                        addinfo.split(",")[0].strip()
                        + " "
                        + addinfo.split(",")[1].strip()
                    )
                    city = addinfo.split(",")[2].strip()
                    state = addinfo.split(",")[3].strip()
            if 'var latitude = "' in line:
                lat = line.split('var latitude = "')[1].split('"')[0]
            if 'var longitude = "' in line:
                lng = line.split('var longitude = "')[1].split('"')[0]


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
