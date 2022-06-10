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

logger = SgLogSetup().get_logger("baptisthealth_net")


def fetch_data():
    locs = []
    url = "https://baptisthealth.net/baptist-sitemap.xml"
    r = session.get(url, headers=headers)
    bad_urls = [
        "https://baptisthealth.net/Locations/Urgent Care",
        "https://baptisthealth.net/Locations/Surgery Centers",
        "https://baptisthealth.net/Locations/Sleep Centers",
        "https://baptisthealth.net/Locations/Rehabilitation Centers",
        "https://baptisthealth.net/Locations/Primary Care",
        "https://baptisthealth.net/Locations/Physician Practices/Urology",
        "https://baptisthealth.net/Locations/Physician Practices/Orthopedics",
        "https://baptisthealth.net/Locations/Physician Practices/Neuroscience",
        "https://baptisthealth.net/Locations/Physician Practices/General Surgery",
        "https://baptisthealth.net/Locations/Physician Practices/Endocrinology",
        "https://baptisthealth.net/Locations/Physician Practices/Cardiovascular",
        "https://baptisthealth.net/Locations/Physician Practices/Cancer",
        "https://baptisthealth.net/Locations/Physician Practices",
        "https://baptisthealth.net/Locations/Hospitals",
        "https://baptisthealth.net/Locations/Endoscopy Centers",
        "https://baptisthealth.net/Locations/Emergency Care",
        "https://baptisthealth.net/Locations/Diagnostic Imaging",
    ]
    website = "baptisthealth.net"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://baptisthealth.net/locations/" in line:
            items = line.split("<loc>https://baptisthealth.net/locations/")
            for item in items:
                if "</loc>" in item and "<urlset xmlns" not in item:
                    lurl = "https://baptisthealth.net/locations/" + item.split("<")[0]
                    if lurl.count("/") >= 5:
                        if lurl not in bad_urls:
                            locs.append(lurl)
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        typ = loc.split("https://baptisthealth.net/locations/")[1].split("/")[0]
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        try:
            r2 = session.get(loc, headers=headers)
            for line2 in r2.iter_lines():
                if '"name": "' in line2 and name == "":
                    name = line2.split('"name": "')[1].split('"')[0]
                if '"telephone": "' in line2:
                    phone = line2.split('"telephone": "')[1].split('"')[0]
                if '"streetAddress": "' in line2:
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if '"addressLocality": "' in line2:
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                if '"addressRegion": "' in line2:
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                if "day:" in line2 and "Hours Today" not in line2:
                    days = line2.split("<br/>")
                    for day in days:
                        day = day.replace("\t", "").strip()
                        if hours == "":
                            hours = day
                        else:
                            hours = hours + "; " + day
            if hours == "":
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            if add != "":
                if "150 Smith Road" in add:
                    state = "<MISSING>"
                add = add.replace(",", "")
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
