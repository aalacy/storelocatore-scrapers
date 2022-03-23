from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("jiffylubeontario_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/x-www-form-urlencoded",
}
headers2 = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    locs = [
        "https://www.jiffylubeontario.com/sudbury-1003-kingsway|P3B 2E6|Sudbury||",
        "https://www.jiffylubeontario.com/sudbury-900-lasalle-boulevard|P3A 5W8|Sudbury||",
        "https://www.jiffylubeontario.com/chelmsford-4764-regional-road-15|P0M 1L0|Chelmsford||",
        "https://www.jiffylubeontario.com/oshawa-581-king-st|L1H 1G3|Oshawa||",
        "https://www.jiffylubeontario.com/oshawa-23-taunton-rd-west|L1G 7B4|Oshawa||",
        "https://www.jiffylubeontario.com/whitby-516-brock-st-n|L1N 4J2|Whitby||",
        "https://www.jiffylubeontario.com/stcatharines-124-hartzel-rd|L2P 1N7|St. Catharines||",
        "https://www.jiffylubeontario.com/niagara-falls-5975-thorold-stone-rd|L2J 1A2|Niagara Falls||",
        "https://www.jiffylubeontario.com/welland-536-niagara-st|L3C 1L8|Welland||",
        "https://www.jiffylubeontario.com/sarnia-763-exmouth-st|N7T 5P7|Sarnia||",
    ]
    url = "https://www.jiffylubeontario.com/wp-admin/admin-ajax.php"
    cities = [
        "Toronto",
        "Ottawa",
        "Mississauga",
        "Brampton",
        "Hamilton",
        "London",
        "Markham",
        "Vaughan",
        "Kitchener",
        "Windsor",
        "Richmond Hill",
        "Oakville",
        "Burlington",
        "Sudbury",
        "Chelmsford",
        "Oshawa",
        "Barrie",
        "St Catharines",
        "Guelph",
        "Cambridge",
        "Whitby",
        "Kingston",
        "Ajax",
        "Milton",
        "Thunder Bay",
        "Waterloo",
        "Chatham Kent",
        "Brantford",
        "Clarington",
        "Pickering",
        "Niagara Falls",
        "Newmarket",
        "Peterborough",
        "Kawartha Lakes",
        "Sault Ste Marie",
        "Sarnia",
        "Caledon",
        "Norfolk County",
        "Halton Hills",
        "Aurora",
        "Welland",
        "North Bay",
        "Belleville",
        "Cornwall",
        "Whitchurch Stouffville",
        "Haldimand County",
        "Georgina",
        "Quinte West",
        "Timmins",
        "Woodstock",
        "St Thomas",
        "Brant",
        "Lakeshore",
        "Innisfil",
        "Bradford West Gwillimbury",
        "New Tecumseth",
        "Stratford",
        "Orillia",
        "Fort Erie",
        "LaSalle",
        "Orangeville",
        "Leamington",
        "Grimsby",
        "Prince Edward County",
        "Clarence Rockland",
        "East Gwillimbury",
        "Lincoln",
        "Tecumseh",
        "Amherstburg",
        "Collingwood",
        "Kingsville",
        "Brockville",
        "Owen Sound",
        "Strathroy Caradoc",
        "Wasaga Beach",
        "Essex",
        "Huntsville",
        "Cobourg",
        "Thorold",
        "Port Colborne",
        "Niagara on the Lake",
        "Middlesex Centre",
        "Petawawa",
        "Pelham",
        "Midland",
        "Port Hope",
        "North Grenville",
        "Bracebridge",
        "Greater Napanee",
        "Tillsonburg",
        "Kenora",
        "West Nipissing",
        "Pembroke",
        "Saugeen Shores",
        "Thames Centre",
        "Mississippi Mills",
        "North Perth",
        "Trent Hills",
        "The Nation",
        "Ingersoll",
        "Central Elgin",
        "West Grey",
        "Gravenhurst",
        "Brighton",
        "Erin",
        "Kincardine",
        "Meaford",
    ]
    coords = []

    for city in cities:
        logger.info("Pulling City %s..." % city)
        payload = {
            "action": "load_map",
            "search[postal]": city,
            "search[config][map_height]": "97px",
            "search[map_case]": "load_locations_from_postal_code",
        }
        r = session.post(url, headers=headers, data=payload)
        count = 0
        try:
            for line in r.iter_lines():
                if "new google.maps.LatLng(" in line and "(0, 0)" not in line:
                    llat = line.split("new google.maps.LatLng(")[1].split(",")[0]
                    llng = (
                        line.split("new google.maps.LatLng(")[1]
                        .split(",")[1]
                        .strip()
                        .split(")")[0]
                    )
                    coords.append(llat + "|" + llng)
                if '<span class="postal">' in line:
                    lc = line.split(",")[0].strip().replace("\t", "")
                    lp = line.split('<span class="postal">')[1].split("<")[0].strip()
                if '<a href="https://www.jiffylubeontario.com/' in line:
                    lurl = line.split('href="')[1].split('"')[0]
                    linfo = lurl + "|" + lp + "|" + lc
                    linfo = (
                        linfo
                        + "|"
                        + coords[count].split("|")[0]
                        + "|"
                        + coords[count].split("|")[1]
                    )
                    if linfo not in locs:
                        locs.append(linfo)
                    count = count + 1
        except:
            pass
    for loc in locs:
        try:
            logger.info("Pulling Location %s..." % loc)
            lurl = loc.split("|")[0]
            zc = loc.split("|")[1]
            city = loc.split("|")[2]
            website = "jiffylubeontario.com"
            country = "CA"
            state = "ON"
            typ = "<MISSING>"
            hours = ""
            add = ""
            lat = loc.split("|")[3]
            lng = loc.split("|")[4]
            phone = ""
            store = "<MISSING>"
            name = ""
            r2 = session.get(lurl, headers=headers2)
            lines = r2.iter_lines()
            hrurl = lurl + "/wp-admin/admin-ajax.php?action=load_hours"
            r3 = session.get(hrurl, headers=headers2)
            lines2 = r3.iter_lines()
            for line3 in lines2:
                if '<span class="textday">' in line3:
                    g = next(lines2)
                    day = g.split("<")[0].strip().replace("\t", "")
                if "<strong>CLOSED</strong>" in line3:
                    day = day + ": CLOSED"
                    if hours == "":
                        hours = day
                    else:
                        hours = hours + "; " + day
                if '<span class="hours-start">' in line3:
                    day = (
                        day
                        + ": "
                        + line3.split('<span class="hours-start">')[1].split("<")[0]
                        + "-"
                        + line3.split('"hours-end">')[1].split("<")[0]
                    )
                    if hours == "":
                        hours = day
                    else:
                        hours = hours + "; " + day
            for line2 in lines:
                if 'itemprop="name address">' in line2:
                    g = next(lines)
                    add = g.split(">")[1].split("<")[0]
                if "class=location-phone>" in line2:
                    phone = line2.split("tel:")[1].split("class")[0].strip()
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split("|")[0].strip()
            if phone == "":
                phone = "<MISSING>"
            name = name.replace("</title>", "").strip()
            name = name.replace("&#8211;", "-").strip()
            if zc == "":
                zc = "<MISSING>"
            if lat == "":
                lat = "<MISSING>"
            if lng == "":
                lng = "<MISSING>"
            if "-514-brock-st-n" in loc:
                add = "514 Brock St N"
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
