from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("earthwisepet_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://www.earthwisepet.com/sitemap.xml"
    locs = ["https://earthwisepet.com/stores/view/yakima"]
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if "<loc>https://earthwisepet.com/stores/view/" in line:
            items = line.split("<loc>https://earthwisepet.com/stores/view/")
            for item in items:
                if "</priority></url><url>" in item:
                    lurl = "https://earthwisepet.com/stores/view/" + item.split("<")[0]
                    if (
                        lurl != "https://earthwisepet.com/stores/view/"
                        and "yakima" not in lurl
                        and "bentleys-pet-stuff-algonquin" not in lurl
                    ):
                        locs.append(lurl)
    logger.info("Found %s Locations." % str(len(locs)))
    for loc in locs:
        name = ""
        add = ""
        city = ""
        state = ""
        store = "<MISSING>"
        lat = "<MISSING>"
        lng = "<MISSING>"
        hours = ""
        country = "US"
        zc = ""
        phone = ""
        logger.info("Pulling Location %s..." % loc)
        website = "earthwisepet.com"
        typ = "Store"
        acount = 0
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            if "<title>" in line2:
                name = line2.split("<title>")[1].split("<")[0]
                if "|" in name:
                    name = name.split("|")[0].strip()
            if '<a tabindex="0" href="https://maps.google.com/?q=' in line2:
                acount = acount + 1
                if acount == 2:
                    addinfo = (
                        line2.split(
                            '<a tabindex="0" href="https://maps.google.com/?q='
                        )[1]
                        .split('"')[0]
                        .strip()
                    )
                    if addinfo.count(",") == 3:
                        add = addinfo.split(",")[0].strip()
                        city = addinfo.split(",")[1].strip()
                        state = addinfo.split(",")[2].strip()
                        zc = addinfo.split(",")[3].strip()
                    else:
                        add = (
                            addinfo.split(",")[0].strip()
                            + " "
                            + addinfo.split(",")[1].strip()
                        )
                        city = addinfo.split(",")[2].strip()
                        state = addinfo.split(",")[3].strip()
                        zc = addinfo.split(",")[4].strip()
            if 'href="tel:' in line2:
                phone = line2.split('href="tel:')[1].split('"')[0].strip()
            if 'google-map" data-lng=' in line2:
                lat = line2.split("data-lat='")[1].split("'")[0]
                lng = line2.split("data-lng='")[1].split("'")[0]
            if 'week-nm">' in line2:
                if hours == "":
                    hours = line2.split('week-nm">')[1].split("<")[0]
                else:
                    hours = hours + "; " + line2.split('week-nm">')[1].split("<")[0]
            if 'timing">' in line2:
                hours = hours + ": " + line2.split('timing">')[1].split("<")[0]
            if 'var latitude = "' in line2:
                lat = line2.split('var latitude = "')[1].split('"')[0]
            if 'var longitude = "' in line2:
                lng = line2.split('var longitude = "')[1].split('"')[0]
        if phone == "":
            phone = "<MISSING>"
        if hours == "":
            hours = "<MISSING>"
        if lat == "":
            lat = "<MISSING>"
        if lng == "":
            lng = "<MISSING>"
        if "woodlands" in loc:
            add = "3570 FM 1488, Ste 500"
            city = "Conroe"
            state = "TX"
            zc = "77384"
            phone = "936-647-1518"
            lat = "30.228852"
            lng = "-95.5184688"
            hours = "<MISSING>"
        if "palmharbor" in loc:
            name = "Palm Harbor"
            add = "3335 Tampa Rd"
            city = "Palm Harbor"
            state = "FL"
            zc = "34684"
            phone = "727-470-9102"
            lat = "28.068362"
            lng = "-82.7235479"
            hours = "<MISSING>"
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
