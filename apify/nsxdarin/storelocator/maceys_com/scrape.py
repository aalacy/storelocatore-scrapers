from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgrequests import SgRequests
from sglogging import SgLogSetup

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("maceys_com")


def fetch_data():
    url = "https://maceys.com/"
    locs = []
    r = session.get(url, headers=headers)
    website = "maceys.com"
    typ = "<MISSING>"
    country = "US"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    hrlist = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<a href="/locations/' in line:
            items = line.split('<a href="/locations/')
            for item in items:
                if '<div class="v-snack__action"><' not in item:
                    lurl = "https://www.maceys.com/locations/" + item.split('"')[0]
                    locs.append(lurl)
    url = "https://afsshareportal.com/lookUpFeatures.php?callback=jsonpcallbackHours&action=storeInfo&website_url=maceys.com&expandedHours=true"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '{"store_id":"' in line:
            items = line.split('{"store_id":"')
            for item in items:
                if (
                    '"store_department_name":"Store"' in item
                    and "jsonpcallbackHours" not in item
                ):
                    sname = item.split('"store_name":"')[1].split('"')[0]
                    shrs = "Sun: " + item.split('"Sunday":"')[1].split('"')[0]
                    shrs = shrs + "; Mon: " + item.split('"Monday":"')[1].split('"')[0]
                    shrs = shrs + "; Tue: " + item.split('"Tuesday":"')[1].split('"')[0]
                    shrs = (
                        shrs + "; Wed: " + item.split('"Wednesday":"')[1].split('"')[0]
                    )
                    shrs = (
                        shrs + "; Thu: " + item.split('"Thursday":"')[1].split('"')[0]
                    )
                    shrs = shrs + "; Fri: " + item.split('"Friday":"')[1].split('"')[0]
                    shrs = (
                        shrs + "; Sat: " + item.split('"Saturday":"')[1].split('"')[0]
                    )
                    shrs = shrs.replace("Closed to Closed", "Closed")
                    slat = item.split('"store_lat":"')[1].split('"')[0]
                    slng = item.split('"store_lng":"')[1].split('"')[0]
                    hrlist.append(sname + "|" + shrs + "|" + slat + "|" + slng)
    for loc in locs:
        logger.info(loc)
        r2 = session.get(loc, headers=headers)
        lines = r2.iter_lines()
        phone = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        name = ""
        hours = "<MISSING>"
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0].replace(" - Macey's", "")
            if 'bold" href="tel:' in line2 and phone == "":
                phone = line2.split('bold" href="tel:')[1].split('"')[0]
            if "Address</h3>" in line2:
                add = (
                    line2.split('<p class="text-body-2 mb-1 font-weight-bold">')[1]
                    .split("<")[0]
                    .strip()
                )
                csz = (
                    line2.split('<p class="text-body-2 mb-1 font-weight-bold">')[1]
                    .split("<br>")[1]
                    .split("</p>")[0]
                )
                csz = csz.replace("\t", "")
                city = csz.split(",")[0]
                state = csz.split(",")[1].strip().split(" ")[0]
                zc = csz.strip().rsplit(" ", 1)[1]
        for item in hrlist:
            if item.split("|")[0] == name:
                hours = item.split("|")[1]
                lat = item.split("|")[2]
                lng = item.split("|")[3]
        if "parleys-" in loc:
            hours = "Mon-Sat: 6 AM to 11 PM; Sunday: 7 AM to 10 PM"
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
