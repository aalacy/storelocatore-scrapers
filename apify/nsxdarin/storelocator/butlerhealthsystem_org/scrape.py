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

logger = SgLogSetup().get_logger("butlerhealthsystem_org")


def fetch_data():
    locs = []
    url = "https://www.butlerhealthsystem.org/Locations.aspx"
    r = session.get(url, headers=headers)
    website = "butlerhealthsystem.org"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if 'ata-longitude="' in line:
            llng = line.split('ata-longitude="')[1].split('"')[0]
            llat = line.split('ata-latitude="')[1].split('"')[0]
        if "More information</a>" in line:
            locs.append(
                "https://www.butlerhealthsystem.org"
                + line.split('href="')[1].split('"')[0]
                + "|"
                + llat
                + "|"
                + llng
            )
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        name = ""
        add = ""
        city = ""
        state = ""
        zc = ""
        store = "<MISSING>"
        phone = ""
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        hours = ""
        HFound = False
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "Hours</strong>" in line2:
                HFound = True
            if HFound and "</div>" in line2:
                HFound = False
            if HFound and "&ndash;" in line2:
                hrs = (
                    line2.strip()
                    .replace("<br>", "")
                    .replace("\n", "")
                    .replace("\r", "")
                    .replace("\t", "")
                    .replace("&ndash;", "-")
                )
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if '<meta itemprop="name" content="' in line2 and name == "":
                name = line2.split('<meta itemprop="name" content="')[1].split('"')[0]
            if 'itemprop="streetAddress" content="' in line2 and add == "":
                add = line2.split('itemprop="streetAddress" content="')[1].split('"')[0]
            if 'itemprop="addressLocality" content="' in line2 and city == "":
                city = line2.split('itemprop="addressLocality" content="')[1].split(
                    '"'
                )[0]
            if 'itemprop="addressRegion" content="' in line2 and state == "":
                state = (
                    line2.split('itemprop="addressRegion" content="')[1]
                    .split('"')[0]
                    .strip()
                )
            if 'itemprop="postalCode" content="' in line2 and zc == "":
                zc = line2.split('itemprop="postalCode" content="')[1].split('"')[0]
            if 'itemprop="telephone" content="' in line2 and phone == "":
                phone = line2.split('itemprop="telephone" content="')[1].split('"')[0]
        if hours == "":
            hours = "<MISSING>"
        hours = (
            hours.replace("<p>", "")
            .replace("</p>", "")
            .replace("<span>", "")
            .replace("</span>", "")
            .strip()
        )
        add = add.replace("Rose E. Schneider Family YMCA<br>", "")
        if "160 Medical Center" in add:
            zc = "16025"
        hours = (
            hours.replace("<strong>", "")
            .replace("</strong>", "")
            .replace("<ul>", "")
            .replace("<li>", "")
            .replace("</ul>", "")
            .replace("</li>", "")
            .replace(":", ": ")
            .replace("  ", " ")
        )
        yield SgRecord(
            locator_domain=website,
            page_url=lurl,
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
