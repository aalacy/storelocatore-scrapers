from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("homegoods_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.homegoods.com/us/store/xml/storeLocatorSiteMap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.homegoods.com/us/store/stores/" in line:
            items = line.split("<loc>https://www.homegoods.com/us/store/stores/")
            for item in items:
                if "xmlns:xhtml" not in item:
                    locs.append(
                        "https://www.homegoods.com/us/store/stores/"
                        + item.split("<")[0]
                    )
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        CS = False
        loc = loc.replace("&#39;", "'")
        add = ""
        city = ""
        state = ""
        zc = ""
        phone = ""
        logger.info("Pulling Location %s..." % loc)
        website = "homegoods.com"
        typ = "Store"
        hours = ""
        name = ""
        lat = ""
        lng = ""
        store = loc.split("/aboutstore")[0].rsplit("/", 1)[1]
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split(":")[0].strip()
                zc = name.rsplit(" ", 1)[1]
            if "new store opening on" in line2.lower():
                CS = True
            if 'type="hidden" name="address" value="' in line2:
                add = (
                    line2.split('type="hidden" name="address" value="')[1]
                    .split('"')[0]
                    .strip()
                )
            if 'type="hidden" name="city" value="' in line2:
                city = line2.split('type="hidden" name="city" value="')[1].split('"')[0]
            if 'type="hidden" name="state" value="' in line2:
                state = line2.split('type="hidden" name="state" value="')[1].split('"')[
                    0
                ]
            if 'type="hidden" name="phone" value="' in line2:
                phone = line2.split('type="hidden" name="phone" value="')[1].split('"')[
                    0
                ]
            if 'type="hidden" name="lat" value="' in line2:
                lat = line2.split('ype="hidden" name="lat" value="')[1].split('"')[0]
            if 'type="hidden" name="long" value="' in line2:
                lng = line2.split('type="hidden" name="long" value="')[1].split('"')[0]
            if 'type="hidden" name="hours" value="' in line2:
                hours = line2.split('type="hidden" name="hours" value="')[1].split('"')[
                    0
                ]
        country = "US"
        add = add.replace("&#39;", "'")
        city = city.replace("&#39;", "'")
        name = name.replace("&#39;", "'")
        if CS is False:
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
