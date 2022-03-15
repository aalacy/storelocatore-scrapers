from sgrequests import SgRequests
from sglogging import SgLogSetup
import time
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("samsclub_com__fuel")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    session = SgRequests()
    url = "https://www.samsclub.com/sitemap_locators.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://www.samsclub.com/club/" in line:
            items = line.split("<loc>https://www.samsclub.com/club/")
            for item in items:
                if '<?xml version="' not in item:
                    lurl = "https://www.samsclub.com/club/" + item.split("<")[0]
                    locs.append(lurl)
    for loc in locs:
        Fuel = False
        logger.info(("Pulling Location %s..." % loc))
        website = "samsclub.com/fuel"
        typ = "Gas"
        hours = ""
        name = ""
        country = "US"
        city = ""
        add = ""
        zc = ""
        state = ""
        lat = ""
        lng = ""
        phone = ""
        session = SgRequests()
        time.sleep(3)
        store = loc.rsplit("/", 1)[1]
        locurl = "https://www.samsclub.com/api/node/clubfinder/" + store
        r2 = session.get(locurl, headers=headers)
        for line2 in r2.iter_lines():
            if '"postalCode":"' in line2 and '"displayName":"Fuel Center"' in line2:
                Fuel = True
                name = line2.split('"isActive":')[1].split('"name":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                try:
                    add = line2.split('"address1":"')[1].split('"')[0]
                except:
                    add = ""
                try:
                    add = add + " " + line2.split('"address2":"')[1].split('"')[0]
                except:
                    pass
                city = line2.split('"city":"')[1].split('"')[0]
                state = line2.split('"state":"')[1].split('"')[0]
                phone = line2.split('"phone":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split("}")[0]
                lng = line2.split('"longitude":')[1].split(",")[0]
                try:
                    fcinfo = line2.split(
                        '"displayName":"Fuel Center","operationalHours":{'
                    )[1].split("}}},")[0]
                    days = fcinfo.split('},"')
                    for day in days:
                        hrs = (
                            day.split('"startHr":"')[1].split('"')[0]
                            + "-"
                            + day.split('"endHr":"')[1].split('"')[0]
                        )
                        dname = day.split('Hrs":')[0].replace('"', "")
                        hrs = dname + ": " + hrs
                        hrs = hrs.replace("To", "-")
                        if hours == "":
                            hours = hrs
                        else:
                            hours = hours + "; " + hrs
                except:
                    hours = ""
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        if Fuel is True and add != "":
            if city == "Columbus" and "5448" in add:
                add = "5448 'A' Whittlesey Blvd"
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
