from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("bjc_org")


def fetch_data():
    locs = []
    url = "https://www.bjc.org/About-Us/Locations"
    r = session.get(url, headers=headers)
    website = "bjc.org"
    country = "US"
    ltyp = "Hospital"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if 'class="tab-pane " id="' in line:
            ltyp = (
                line.split('class="tab-pane " id="')[1]
                .split('"')[0]
                .replace("-", " ")
                .title()
            )
        if "more information" in line.lower() and "href=" in line:
            locs.append(line.split('href="')[1].split('"')[0] + "|" + ltyp)
    for loc in locs:
        lurl = loc.split("|")[0]
        logger.info(lurl)
        typ = loc.split("|")[1]
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
        hours2 = ""
        r2 = session.get(lurl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<h1>" in line2:
                name = line2.split("<h1>")[1].split("<")[0]
            if 'lass="address">' in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                add = g.split("<")[0].strip().replace("\t", "")
                addinfo = (
                    h.strip().replace("\t", "").replace("\r", "").replace("\n", "")
                )
                try:
                    city = addinfo.split(",")[0]
                    state = addinfo.split(",")[1].rsplit(" ", 1)[0]
                    zc = addinfo.rsplit(" ", 1)[1]
                except:
                    city = ""
                    state = ""
                    zc = ""
            if "<a href=tel:" in line2:
                phone = line2.split("<a href=tel:")[1].split(">")[1].split("<")[0]
            if '"closes": "' in line2:
                hc = line2.split('"closes": "')[1].split('"')[0]
            if '"dayOfWeek": "http://schema.org/' in line2:
                day = line2.split('"dayOfWeek": "http://schema.org/')[1].split('"')[0]
            if '"opens": "' in line2:
                ho = line2.split('"opens": "')[1].split('"')[0]
                hrs = day + ": " + ho + "-" + hc
                hrs = hrs.replace("00:00:00-00:00:00", "Closed")
                if hours == "":
                    hours = hrs
                else:
                    hours = hours + "; " + hrs
            if "Operating Hours:</strong><br><strong>" in line2:
                hours2 = line2.split("Operating Hours:</strong><br><strong>")[1].split(
                    "</p><"
                )[0]
        if hours == "":
            hours = "<MISSING>"
        if hours2 != "":
            hours = hours2
        hours = hours.replace("</strong>", "")
        hours = hours.replace("</strong><br><strong>", "; ")
        hours = hours.replace(":00;", ";").replace(":00-", "-")
        city = city.replace("&#39;", "'")
        add = add.replace("&#39;", "'")
        name = name.replace("&#39;", "'")
        city = city.replace("&amp;", "&")
        add = add.replace("&amp;", "&")
        name = name.replace("&amp;", "&")
        hours = hours.replace("<br><strong>", "; ")
        if phone == "":
            phone = "<MISSING>"
        if "Eunice-Smith-Home" in lurl:
            name = "Alton Memorial Rehabilitation & Therapy"
            add = "1251 College Avenue"
            city = "Alton"
            state = "IL"
            zc = "62002"
            phone = "618-463-7330"
        if "Barnes-Jewish-Extended-Care" in lurl:
            name = "Barnes-Jewish Extended Care"
            city = "Clayton"
            state = "MO"
            phone = "314-725-7447"
            add = "401 Corporate Park Drive"
            zc = "63105"
        if "Christian-Extended-Care-Rehabilitation" in lurl:
            name = "Christian Extended Care & Rehabilitation"
            city = "St. Louis"
            state = "MO"
            zc = "63136"
            phone = "314-653-4848"
            add = "11160 Village Drive North"
        if "Memorial-Care-Center" in lurl:
            name = "Memorial Care Center"
            add = "4315 Memorial Drive"
            city = "Belleville"
            state = "IL"
            zc = "62226"
            phone = "618-619-5000"
        if "Transitional-Care-Program" in lurl:
            name = "Transitional Care Program"
            city = "Sullivan"
            state = "MO"
            zc = "63080"
            add = "751 Sappington Bridge Road"
            phone = "573-468-1191"
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
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.PAGE_URL,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
