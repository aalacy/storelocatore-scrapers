from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("aspencreekgrill_com")


session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://aspencreekgrill.com/"
    locs = []
    r = session.get(url, headers=headers, verify=False)
    if r.encoding is None:
        r.encoding = "utf-8"
    Found = False
    for line in r.iter_lines(decode_unicode=True):
        if '<ul class="sub-menu">' in line and len(locs) == 0:
            Found = True
        if Found and "Menus</a>" in line:
            Found = False
        if Found and 'href="https://aspencreekgrill.com/' in line:
            lurl = line.split('href="')[1].split('"')[0]
            if (
                "-menu" not in lurl
                and lurl not in locs
                and "uploads" not in lurl
                and "/cart" not in lurl
                and "contact-" not in lurl
                and "terms" not in lurl
                and "blackhole" not in lurl
            ):
                locs.append(lurl)
    logger.info(("Found %s Locations." % str(len(locs))))
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        store = ""
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        country = ""
        zc = ""
        phone = ""
        logger.info(("Pulling Location %s..." % loc))
        website = "aspencreekgrill.com"
        typ = "Restaurant"
        r2 = session.get(loc, headers=headers)
        if r2.encoding is None:
            r2.encoding = "utf-8"
        lines = r2.iter_lines(decode_unicode=True)
        for line2 in lines:
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if "Address</span></h4>" in line2:
                g = next(lines).replace("<span>", "").replace("</span>", "")
                if "<p>" in g:
                    add = g.split("<p>")[1].split("<")[0]
                    city = g.split("<br />")[1].split(",")[0].strip()
                    zc = g.split("</p>")[0].rsplit(" ", 1)[1]
                    state = g.split("<br />")[1].split(",")[1].strip().split(" ")[0]
                else:
                    add = g.split('">')[1].split("<")[0]
                    g = next(lines)
                    city = g.split(",")[0]
                    zc = g.split("<")[0].rsplit(" ", 1)[1]
                    state = g.split("<")[0].rsplit(" ", 1)[0]
                country = "US"
                store = "<MISSING>"
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0]
            if "Hours</span></h4>" in line2:
                g = next(lines)
                if "<p>" in g:
                    hours = g.split("<p>")[1].split("</p>")[0].replace("<br />", "; ")
                else:
                    hours = g.split('">')[1].split("<")[0]
                    hours = hours + "; " + next(lines).split("<")[0].strip()
            if "CALL AHEAD:" in line2:
                phone = line2.split("CALL AHEAD:")[1].split("<")[0].strip()
        if "<" in zc:
            zc = zc.split("<")[0]
        hours = hours.replace("&amp;", "&").replace("&#8211;", "-")
        if "<" in hours:
            hours = hours.split("<")[0].strip()
        if "KENTUCKY" in state:
            state = "KENTUCKY"
        if "/tyler" in loc:
            add = "1725 W SW Loop 323"
            city = "Tyler"
            state = "Texas"
            zc = "75701"
        phone = "<MISSING>"
        store = "<MISSING>"
        country = "US"
        if (
            "/star" not in loc
            and city != "<MISSING>"
            and "campfire-cocktails" not in loc
            and "harvest" not in loc
        ):
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
