from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("onemedical_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = []
    url = "https://www.onemedical.com/locations/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'href="/locations/' in line and "tabindex" not in line:
            code = line.split("/locations/")[1].split('"')[0]
            lurl = "https://www.onemedical.com/api/locations/?code=" + code
            logger.info(("Pulling Region %s..." % code))
            r2 = session.get(lurl, headers=headers)
            for line2 in r2.iter_lines():
                if '"latitude\\": ' in line2:
                    items = line2.split('"latitude\\": ')
                    for item in items:
                        if '"slug\\": \\"' in item:
                            iadd = (
                                item.split('"address1\\": \\"')[1].split("\\")[0]
                                + " "
                                + item.split('"address2\\": \\"')[1].split("\\")[0]
                            )
                            iadd = iadd.strip()
                            ilat = item.split(",")[0]
                            ilng = item.split('\\"longitude\\": ')[1].split(",")[0]
                            locs.append(
                                "https://www.onemedical.com/locations/"
                                + code
                                + "/"
                                + item.split('"slug\\": \\"')[1].split("\\")[0]
                                + "|"
                                + ilat
                                + "|"
                                + ilng
                                + "|"
                                + iadd
                            )
    for loc in locs:
        logger.info(("Pulling Location %s..." % loc.split("|")[0]))
        website = "onemedical.com"
        purl = loc.split("|")[0]
        if "chi/oakbrookpromenade-modernaavailable" in purl:
            purl = "https://www.onemedical.com/locations/chi/oakbrookpromenade/"
        typ = "<MISSING>"
        hours = ""
        name = ""
        add = ""
        city = ""
        state = ""
        country = "US"
        lat = loc.split("|")[1]
        lng = loc.split("|")[2]
        add = loc.split("|")[3]
        store = "<MISSING>"
        hours = ""
        phone = ""
        zc = ""
        r2 = session.get(purl, headers=headers)
        lines = r2.iter_lines()
        for line2 in lines:
            if "<title>" in line2 and name == "":
                name = line2.split("<title>")[1].split(" |")[0]
            if '<p itemprop="telephone"><a href="tel:' in line2:
                phone = line2.split('<p itemprop="telephone"><a href="tel:')[1].split(
                    '"'
                )[0]
            if '<span itemprop="addressLocality">' in line2:
                city = line2.split('<span itemprop="addressLocality">')[1].split("<")[0]
            if '<span itemprop="addressRegion">' in line2:
                state = line2.split('<span itemprop="addressRegion">')[1].split("<")[0]
            if '<span itemprop="postalCode">' in line2:
                zc = line2.split('<span itemprop="postalCode">')[1].split("<")[0]
            if "Office Hours:</h5>" in line2:
                g = next(lines)
                hours = (
                    g.split('<div class="rich-text">')[1]
                    .split("</div")[0]
                    .replace("<br>", "; ")
                )
        if "<br/>" in hours:
            hours = hours.split("<br/>")[0]
        if hours == "":
            hours = "<MISSING>"
        if phone == "":
            phone = "<MISSING>"
        hours = hours.replace("Primary Care:", "").strip()
        if "<br" in hours:
            hours = hours.split("<br")[0]
        if "(check" in hours:
            hours = hours.split("(check")[0]
        if "**" in hours:
            hours = hours.split("**")[0].strip()
        if "; ;" in hours:
            hours = hours.split("; ;")[0].strip()
        if " Current" in hours:
            hours = hours.split(" Current")[0].strip()
        if " - Lab" in hours:
            hours = hours.split(" - Lab")[0].strip()
        if "; The " in hours:
            hours = hours.split("; The")[0].strip()
        if " (" in hours:
            hours = hours.split(" (")[0].strip()
        if "; Wednesday 3" in hours:
            hours = hours.split("; Wednesday 3")[0].strip()
        if "Closed every" in hours:
            hours = "Temporarily Closed"
        yield SgRecord(
            locator_domain=website,
            page_url=purl,
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
