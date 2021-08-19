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

logger = SgLogSetup().get_logger("powerhousegym_com")


def fetch_data():
    url = (
        "https://powerhousegym.com/locations/?country=united-states&zip_code=&radius=25"
    )
    r = session.get(url, headers=headers)
    locs = []
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if '<h3><a href="https://powerhousegym.com/locations/' in line:
            lurl = line.split('<h3><a href="')[1].split('"')[0]
            if "-japan" not in lurl:
                locs.append(lurl)
    for loc in locs:
        r2 = session.get(loc, headers=headers)
        logger.info(loc)
        website = "powerhousegym.com"
        typ = "<MISSING>"
        country = "US"
        hours = ""
        store = "<MISSING>"
        add = "<MISSING>"
        city = "<MISSING>"
        state = "<MISSING>"
        zc = "<MISSING>"
        if "canada" in url:
            country = "CA"
        lines = r2.iter_lines()
        for line2 in lines:
            line2 = str(line2.decode("utf-8"))
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
            if "Location</p>" in line2:
                next(lines)
                g = next(lines)
                h = next(lines)
                g = str(g.decode("utf-8"))
                h = str(h.decode("utf-8"))
                if 'small"></p>' not in g:
                    try:
                        if '"grey-text light small">' in g:
                            addinfo = g.split('"grey-text light small">')[1].split("<")[
                                0
                            ]
                        else:
                            addinfo = (
                                g.split(">")[1]
                                .strip()
                                .replace("\r", "")
                                .replace("\t", "")
                                .replace("\n", "")
                            )
                        addinfo = addinfo + "|" + h.split("<")[0].strip()
                        add = addinfo.split("|")[0]
                        csz = addinfo.split("|")[1]
                        city = csz.split(",")[0]
                        state = csz.split(",")[1].strip().split(" ")[0]
                        zc = csz.rsplit(" ", 1)[1]
                    except:
                        pass
            if '<a href="tel:' in line2:
                phone = line2.split('<a href="tel:')[1].split('"')[0]
            if '"latitude":' in line2:
                lat = line2.split('"latitude":')[1].split(",")[0]
                lng = line2.split('"longitude":')[1].split("}")[0]
            if "Gym Hours</p>" in line2:
                next(lines)
                g = next(lines)
                g = str(g.decode("utf-8"))
                while "Special Offers</p>" not in g and "<" in g:
                    hrs = (
                        g.replace('<p class="grey-text light small">', "")
                        .replace("<br />", "")
                        .replace("</p>", "")
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                        .strip()
                    )
                    if hours == "":
                        hours = hrs
                    else:
                        hours = hours + "; " + hrs
                    g = next(lines)
                    g = str(g.decode("utf-8"))
        if "</p" in add:
            add = add.split("</p")[0]
        if "," in name and "Coming Soon" not in hours:
            sname = name.rsplit(",", 1)[1].strip()
            if len(sname) == 2:
                state = sname
                city = name.split(",")[0].strip()
                if " " in add:
                    zc = add.rsplit(" ", 1)[1]
                if "," in add:
                    add = add.split(",")[0].strip()
                if "aldergrove-bc" in loc:
                    country = "CA"
                    zc = "V4W 2X3"
                    state = "BC"
                    city = "Aldergrove"
                if "west-bloomfield" in loc:
                    zc = "48323"
                if "/syracuse" in loc:
                    zc = "<MISSING>"
                if "locations/aurora" in loc:
                    zc = "80014"
                add = add.replace(zc, "").strip()
                citystring = " " + city
                citystring2 = " " + city + " "
                if citystring2 not in add:
                    add = add.replace(citystring, "").strip()
                if "</b>; Mon" in hours:
                    hours = "Mon" + hours.split("</b>; Mon")[1]
                if "More Info:" in hours:
                    hours = "<MISSING>"
                if ":; ; Mon" in hours:
                    hours = "Mon" + hours.split(":; ; Mon")[1]
                hours = hours.replace("; ; Staff", "; Staff")
                if "pm; ;" in hours:
                    hours = hours.split("pm; ;")[0] + "pm"
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
