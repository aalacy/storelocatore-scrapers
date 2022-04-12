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

logger = SgLogSetup().get_logger("badaxethrowing_com")


def fetch_data():
    locs = []
    url = "https://badaxethrowing.com/locations/"
    r = session.get(url, headers=headers)
    website = "badaxethrowing.com"
    typ = "<MISSING>"
    Found = False
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://order.capriottis.com/menu/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
        if "UK</a>" in line:
            Found = True
        if 'class="menu-country' in line:
            country = line.split('#">')[1].split("<")[0]
            if country == "UK":
                country = "GB"
        if (
            Found
            and 'class="menu-item menu-item-type-post_type menu-item-object-pag' in line
        ):
            locs.append(line.split('href="')[1].split('"')[0] + "|" + country)
        if Found and "Our Locations" in line:
            Found = False
    for loc in locs:
        country = loc.split("|")[1]
        lurl = loc.split("|")[0]
        CS = False
        if lurl != "https://badaxethrowing.com/locations/":
            logger.info(lurl)
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
            r2 = session.get(lurl, headers=headers)
            for line2 in r2.iter_lines():
                if "coming soon" in line2 and "wide variety coming soon" not in line2:
                    CS = True
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("<")[0]
                    if " |" in name:
                        name = name.split(" |")[0]
                if '"streetAddress">' in line2:
                    add = line2.split('"streetAddress">')[1].split("<")[0]
                    zc = add.rsplit(" ", 1)[1]
                    add = add.split(",")[0]
                if '"streetAddress": "' in line2:
                    addfull = line2.split('"streetAddress": "')[1].split('"')[0]
                    if "," in addfull:
                        add = addfull.split(",")[0]
                    else:
                        add = addfull
                    try:
                        zc = addfull.rsplit(" ", 1)[1]
                    except:
                        zc = "<MISSING>"
                if '"addressLocality": "' in line2:
                    city = line2.split('"addressLocality": "')[1].split('"')[0]
                if '"addressRegion": "' in line2:
                    state = line2.split('"addressRegion": "')[1].split('"')[0]
                if '"addressLocality" content="' in line2:
                    city = line2.split('"addressLocality" content="')[1].split('"')[0]
                if '"addressRegion" content="' in line2:
                    state = line2.split('"addressRegion" content="')[1].split('"')[0]
                if '"telephone": "' in line2:
                    phone = line2.split('"telephone": "')[1].split('"')[0]
            hours = "Mon-Sun: 8:00AM-11:00PM"
            if city == "London" and country == "GB":
                state = "<MISSING>"
                zc = "HA9 0JT"
                add = "Boxpark Wembley, Units 32&33, 18 Olympic Way"
                city = "Wembley"
            if "Windsor" in name:
                add = "2451 Dougall Ave"
                city = "Windsor"
                state = "ON"
                zc = "N8X 1T3"
            name = name.replace("&amp;", "&")
            if "https://badaxethrowing.com/locations/axe-throwing-burlington" in loc:
                zc = "<MISSING>"
            if "https://badaxethrowing.com/locations/axe-throwing-kitchener" in loc:
                zc = "<MISSING>"
            if (
                "ottawa" in loc
                or "mississ" in loc
                or "vaughan" in loc
                or "waterloo" in loc
                or "surrey" in loc
                or "winnipeg" in loc
            ):
                zc = "<MISSING>"
            if CS is False:
                if (
                    "0" not in zc
                    and "1" not in zc
                    and "2" not in zc
                    and "3" not in zc
                    and "4" not in zc
                    and "5" not in zc
                    and "6" not in zc
                    and "7" not in zc
                    and "8" not in zc
                ):
                    zc = "<MISSING>"
                if "#" in zc:
                    zc = "<MISSING>"
                if "Evarts St" in add:
                    zc = "20018"
                if "30 Hill St" in add:
                    zc = "94014"
                if "Minneapolis" in name:
                    city = "Minneapolis"
                if "axe-throwing-surrey" in loc:
                    add = "8132, 109 130 St #109"
                if "axe-throwing-vaughan" in loc:
                    add = "171, 3 Maplecrete Rd #3"
                if "axe-throwing-winnipeg" in loc:
                    add = "1393, 6 Border St #6"
                if "axe-throwing-burlington" in loc:
                    zc = "L7R 2E4"
                if "axe-throwing-mississauga/" in loc:
                    zc = "L4W 1J8"
                if "-throwing-ottawa" in loc:
                    zc = "K1B 4L2"
                if "axe-throwing-surrey" in loc:
                    zc = "V3W 8J9"
                if "throwing-vaughan" in loc:
                    zc = "L4K 2B4"
                if "xe-throwing-waterloo" in loc:
                    zc = "N2J 3H8"
                if "/axe-throwing-winnipeg" in loc:
                    zc = "R3H 0N1"
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
