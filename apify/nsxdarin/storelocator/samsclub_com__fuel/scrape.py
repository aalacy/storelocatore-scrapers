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
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if 'Name":"Fuel Center","name":"GAS"' in line:
                Fuel = True
                mf = line.split('Name":"Fuel Center","name":"GAS"')[1].split('"monToFriHrs":{"startHrs":"')[1].split('"')[0] + '-' + line.split('Name":"Fuel Center","name":"GAS"')[1].split('"monToFriHrs":{"')[1].split('"endHrs":"')[1].split('"')[0]
                sat = line.split('Name":"Fuel Center","name":"GAS"')[1].split('"saturdayHrs":{"startHrs":"')[1].split('"')[0] + '-' + line.split('Name":"Fuel Center","name":"GAS"')[1].split('"saturdayHrs":{"')[1].split('"endHrs":"')[1].split('"')[0]
                sun = line.split('Name":"Fuel Center","name":"GAS"')[1].split('"sundayHrs":{"startHrs":"')[1].split('"')[0] + '-' + line.split('Name":"Fuel Center","name":"GAS"')[1].split('"sundayHrs":{"')[1].split('"endHrs":"')[1].split('"')[0]
                hours = 'Mon-Fri: ' + mf + '; Sat: ' + sat + '; Sun: ' + sun
            if '"clubDetails":' in line:
                name = line.split('"clubDetails":')[1].split('"name":"')[1].split('"')[0]
                add = line.split('"address1":"')[1].split('"')[0]
                city = line.split('"city":"')[1].split('"')[0]
                zc = line.split('postalCode":"')[1].split('"')[0]
                state = line.split('state":"')[1].split('"')[0]
                phone = line.split('"phone":"')[1].split('"')[0]
                lat = line.split('"latitude":')[1].split('"')[0]
                lng = line.split('"longitude":')[1].split('}')[0]
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
