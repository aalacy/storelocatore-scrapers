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

logger = SgLogSetup().get_logger("applebeescanada_com")


def fetch_data():
    locs = []
    url = "https://applebeescanada.com/locations/"
    r = session.get(url, headers=headers)
    website = "applebeescanada.com"
    typ = "<MISSING>"
    country = "CA"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '"tb-button__link" href="https://applebeescanada.com/location/' in line:
            locs.append(line.split('"tb-button__link" href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = ""
        lng = ""
        hours = ""
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<h1 class="tb-heading has-text-color"' in line2:
                name = (
                    line2.split('<h1 class="tb-heading has-text-color"')[1]
                    .split('">')[1]
                    .split("<")[0]
                    .replace("&#8217;", "'")
                    .replace("&#8211;", "-")
                )
            if (
                '<div class="tb-field" data-toolset-blocks-field="' in line2
                and add == ""
            ):
                addinfo = (
                    line2.split('<div class="tb-field" data-toolset-blocks-field="')[1]
                    .split('">')[1]
                    .split("<")[0]
                )
                addinfo = addinfo.replace("Falls ON", "Falls, ON")
                addinfo = addinfo.replace("Canada", "").replace("  ", " ")
                addinfo = addinfo.replace("ON,", "ON")
                if "388 Country Hills Blvd" in addinfo:
                    add = "388 Country Hills Blvd NE #707"
                    city = "Calgary"
                    state = "AB"
                    zc = "T3K 5J6"
                else:
                    add = addinfo.split(",")[0].strip()
                    city = addinfo.split(",")[1].strip()
                    state = addinfo.split(",")[2].strip().split(" ")[0]
                    zc = addinfo.split(",")[2].strip().split(" ", 1)[1]
                if add == "Regina":
                    state = "SK"
                    city = "Regina"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Thunder Bay":
                    state = "ON"
                    city = "Thunder Bay"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Niagara Falls":
                    state = "ON"
                    city = "Niagara Falls"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Winnipeg":
                    city = "Winnipeg"
                    state = "MB"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Brandon":
                    city = "Brandon"
                    state = "MB"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
                if add == "Ajax":
                    city = "Ajax"
                    state = "ON"
                    add = addinfo.split(",")[1].strip()
                    zc = addinfo.split(",")[2].strip()
            if "Call:</strong>&nbsp;&nbsp;" in line2:
                phone = line2.split("Call:</strong>&nbsp;&nbsp;")[1].split("<")[0]
            if 'data-markerlat="' in line2:
                lat = line2.split('data-markerlat="')[1].split('"')[0]
                lng = line2.split('data-markerlon="')[1].split('"')[0]
            if "day:" in line2:
                hrs = line2.rsplit("<", 1)[0]
                if ">" in hrs:
                    hrs = hrs.rsplit(">", 1)[1]
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if "location/applebees-thunderbay" in loc:
            hours = "Sun-Sat: 11:30 AM to 8:00 PM"
        if "huron-church" in loc:
            phone = "519-972-3000"
            name = "Applebee's Huron Church"
            add = "2187 Huron Church Road, Unit 240"
            city = "Windsor"
            state = "ON"
            zc = "<MISSING>"
            lat = "42.275843"
            lng = "-83.052079"
        if "applebees-crossroads" in loc:
            hours = "Sun-Sat: 11:30 PM to 9:00 PM"
        hours = hours.replace(": :", ":")
        if "applebees-niagara-falls" in loc:
            hours = "Sunday to Thursday: 8:00 AM to 10:00 PM; Friday to Saturday: 8:00 AM to 11:00 PM"
        if "(" in hours:
            hours = hours.split("(")[0].strip()
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
