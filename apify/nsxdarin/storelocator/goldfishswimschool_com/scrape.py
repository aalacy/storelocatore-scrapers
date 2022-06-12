from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("goldfishswimschool_com")


def fetch_data():
    locs = []
    url = "https://www.goldfishswimschool.com/sitemap.xml"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "/pricing/</loc>" in line:
            lurl = line.split("<loc>")[1].split("/pricing")[0]
            locs.append(lurl)
    website = "goldfishswimschool.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for loc in locs:
        logger.info(loc)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        daycount = 0
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if '<strong class="blk">' in line2 and add == "":
                add = (
                    line2.split('<strong class="blk">')[1]
                    .replace(", #", " #")
                    .replace(",Ste", "Ste")
                    .replace(",Suite", "Suite")
                    .replace(", Ste", " Ste")
                    .replace(", Suite", " Suite")
                    .split(",")[0]
                )
                zc = (
                    line2.split('<strong class="blk">')[1]
                    .split("<")[0]
                    .strip()
                    .rsplit(" ", 1)[1]
                )
                state = (
                    line2.split('<strong class="blk">')[1]
                    .split("<")[0]
                    .rsplit(",", 1)[1]
                    .strip()
                    .split(" ")[0]
                )
            if '<span itemprop="telephone">' in line2:
                phone = line2.rsplit('">', 1)[1].split("<")[0]
            if '<strong class="pd_bt-20 rlt blk fnt_t-3 fnt_tc-1">' in line2:
                name = line2.split(
                    '<strong class="pd_bt-20 rlt blk fnt_t-3 fnt_tc-1">'
                )[1].split("<")[0]
                city = name.split("School - ")[1].strip()
            if "day:" in line2:
                daycount = daycount + 1
                hrs = (
                    line2.strip().replace("\r", "").replace("\n", "").replace("\t", "")
                )
                if daycount <= 7:
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
        if hours == "":
            hours = "<MISSING>"
        if '<span style="background-color' in hours:
            hours = "<MISSING>"
        if "To Learn More About Our School, Call Today:" in hours:
            hours = "<MISSING>"
        if name != "":
            if "burlington-ont" in loc:
                zc = "L7M 4X7"
            if "/oakville" in loc:
                zc = "L6H 2R4"
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
