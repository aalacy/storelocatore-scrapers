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

logger = SgLogSetup().get_logger("mastrosrestaurants_com")


def fetch_data():
    locs = []
    url = "https://www.mastrosrestaurants.com/view-all-locations/"
    r = session.get(url, headers=headers)
    website = "mastrosrestaurants.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if '{"@type": "FoodEstablishment"' in line:
            items = line.split('{"@type": "FoodEstablishment"')
            for item in items:
                if '"photo":' in item:
                    locs.append(item.split('"url": "')[1].split('"')[0])
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
        CS = False
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if ">COMING SOON!<" in line2:
                CS = True
            if "<title>" in line2:
                name = line2.split("<title>")[1].split(" |")[0]
            if ",<br>" in line2:
                add = line2.split(",<br>")[0].strip().replace("\t", "")
                city = line2.split(",<br>")[1].split(",")[0].strip()
                state = (
                    line2.split(",<br>")[1].strip().split(",")[1].strip().split(" ")[0]
                )
                zc = (
                    line2.replace("\t", "")
                    .replace("\r", "")
                    .replace("\n", "")
                    .rsplit(" ", 1)[1]
                )
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if 'gmaps-lat="' in line2:
                lat = line2.split('gmaps-lat="')[1].split('"')[0]
                lng = line2.split('-lng="')[1].split('"')[0]
            if "PM -" in line2 and "</p><p>" in line2 and hours == "":
                hours = (
                    line2.split("</p><p>")[1].split("<br/><")[0].replace("<br/>", "; ")
                )
            if "<h4>Live Music is Back!</h4><p>" in line2:
                hours = (
                    line2.split("<h4>Live Music is Back!</h4><p>")[1]
                    .split("<strong>")[0]
                    .replace("<br>", "; ")
                )
        if "; Lounge" in hours:
            hours = hours.split("; Lounge")[0]
        if "; Join" in hours:
            hours = hours.split("; Join")[0]
        if "</h4><p>" in hours:
            hours = hours.split("</h4><p>")[1]
        if "<br><button" in hours:
            hours = hours.split("<br><button")[0]
        hours = (
            hours.replace("<strong>", "").replace("</strong>", "").replace("<br>", "; ")
        )
        if "; <" in hours:
            hours = hours.split("; <")[0].strip()
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
