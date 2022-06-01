from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()

logger = SgLogSetup().get_logger("sixt_com")

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    states = []
    url = "https://www.sixt.com/car-rental/#/"
    r = session.get(url, headers=headers)
    website = "sixt.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    Found = False
    for line in r.iter_lines():
        if "States</span>" in line:
            Found = True
        if Found and "Europe</span>" in line:
            Found = False
        if Found and '<a href="/car-rental/usa/' in line:
            surl = (
                "https://www.sixt.com/car-rental/usa/"
                + line.split('<a href="/car-rental/usa/')[1].split('"')[0]
            )
            states.append(surl)
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'locationLink:  "' in line2:
                locs.append(
                    "https://www.sixt.com"
                    + line2.split('locationLink:  "')[1].split('"')[0]
                )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0].strip()
            if "orlando-lake-buena-vista" in loc:
                add = "12205 S Apopka Vineland Rd"
                city = "Orlando"
                state = "FL"
                zc = "32836-6804"
                lat = "28.386945724487"
                lng = "-81.504974365234"
                hours = "MO - FR: 07:00 - 18:00; SA - SU: 09:00 - 17:00"
            if '"streetAddress":"' in line2:
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                zc = line2.split('"postalCode":"')[1].split('"')[0]
                city = line2.split('"addressLocality":"')[1].split('"')[0]
                add = line2.split('"streetAddress":"')[1].split('"')[0]
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
            if "<h2>Sixt Services" in line2:
                htext = line2.split("<h2>Sixt Services")[1].split("<")[0]
                if "," in htext:
                    state = htext.split(",")[1].strip()
                else:
                    state = "<MISSING>"
            if '"openingHours":[' in line2:
                hours = line2.split('"openingHours":[')[1].split('"]')[0]
                hours = hours.replace('"24-hour return","', "")
                if '","HOLIDAYS' in hours:
                    hours = hours.split('","HOLIDAYS')[0]
                hours = hours.replace('","', "; ")
                hours = hours.replace('"', "")
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

    locs = []
    states = []
    url = "https://www.sixt.com/car-rental/united-kingdom/#/"
    r = session.get(url, headers=headers)
    website = "sixt.com"
    typ = "<MISSING>"
    country = "GB"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<h3>SIXT IN United Kingdom</h3>" in line:
            Found = True
        if Found and '<a href="/car-rental/united-kingdom/' in line:
            surl = (
                "https://www.sixt.com/car-rental/united-kingdom/"
                + line.split('<a href="/car-rental/united-kingdom/')[1].split('"')[0]
            )
            states.append(surl)
        if Found and "<span>search</span>" in line:
            Found = False
    for state in states:
        logger.info(state)
        r2 = session.get(state, headers=headers)
        for line2 in r2.iter_lines():
            if 'locationLink:  "' in line2:
                locs.append(
                    "https://www.sixt.com"
                    + line2.split('locationLink:  "')[1].split('"')[0]
                )
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = "<MISSING>"
        zc = ""
        store = "<MISSING>"
        phone = "<MISSING>"
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        try:
            for line2 in r2.iter_lines():
                if '"streetAddress":"' in line2:
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    zc = line2.split('"postalCode":"')[1].split('"')[0]
                    city = line2.split('"addressLocality":"')[1].split('"')[0]
                    add = line2.split('"streetAddress":"')[1].split('"')[0]
                    lat = line2.split('"latitude":')[1].split(",")[0]
                    lng = line2.split('"longitude":')[1].split("}")[0]
        except:
            pass
        if "hilton-park-lane" in loc:
            name = "LONDON PARK LANE CAR RENTAL"
            add = "22 Park Lane"
            state = "<MISSING>"
            zc = "W1K 1BE"
            city = "London"
            lat = "51.155784606934"
            lng = "-0.15942700207233"
            hours = "24 HRS RETURN; MO - FR: 08:00 - 16:00; SA - SU: 08:00 - 13:00; BANK HOLIDAY: 08:00 - 13:00"
        if "n/london-wembley" in loc:
            name = "LONDON WEMBLEY (NORTH) CAR RENTAL"
            add = "GEC Est. Courtenay Rd.,East Ln"
            state = "<MISSING>"
            zc = "HA9 7ND"
            city = "London"
            lat = "51.155784606934"
            lng = "-0.15942700207233"
            hours = "24 HRS RETURN; MO - FR: 08:00 - 18:00; SA - SU: 08:00 - 13:00; BANK HOLIDAY: 08:00 - 13:00"
        if '"openingHours":[' in line2:
            hours = line2.split('"openingHours":[')[1].split('"]')[0]
            hours = hours.replace('"24-hour return","', "")
            if '","HOLIDAYS' in hours:
                hours = hours.split('","HOLIDAYS')[0]
            hours = hours.replace('","', "; ")
            hours = hours.replace('"', "")
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
