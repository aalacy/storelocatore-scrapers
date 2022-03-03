from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgpostal import parse_address_intl

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("fairmont_com")


def fetch_data():
    locs = []
    url = "https://www.fairmont.com"
    r = session.get(url, headers=headers)
    website = "fairmont.com"
    typ = "<MISSING>"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if 'United States</p><ul class="property-list">' in line:
            uslist = (
                line.split('United States</p><ul class="property-list">')[1]
                .split('<div class="property-list-holder"')[0]
                .split('<a href = "')
            )
            for item in uslist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|US")
            calist = (
                line.split('Canada</p><ul class="property-list">')[1]
                .split('<div class="property-list-holder"')[0]
                .split('<a href = "')
            )
            for item in calist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|CA")
            uklist = (
                line.split('>United Kingdom</p><ul class="property-list">')[1]
                .split('d="Middle_East_and_A')[0]
                .split('<a href = "')
            )
            for item in uklist:
                if "</a></li>" in item:
                    locs.append("https://www.fairmont.com" + item.split('"')[0] + "|GB")
    intllocs = []
    url = "https://www.fairmont.com/destinations/"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if 'li class="property-link"><a href = "/' in line:
            items = line.split('li class="property-link"><a href = "/')
            for item in items:
                if '<h2 class="sr-only">North America' not in item:
                    lurl = "https://www.fairmont.com/" + item.split('"')[0]
                    if lurl not in locs and lurl not in intllocs:
                        intllocs.append(lurl)
    for loc in locs:
        purl = loc.split("|")[0]
        country = loc.split("|")[1]
        logger.info(purl)
        name = ""
        add = ""
        city = ""
        if country == "GB":
            state = "<MISSING>"
        zc = ""
        store = ""
        phone = ""
        lat = ""
        lng = ""
        hours = "<MISSING>"
        try:
            r2 = session.get(purl, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if "'hotelname' : '" in line2:
                    name = line2.split("'hotelname' : '")[1].split("'")[0]
                if "'hotelcode' : '" in line2:
                    store = line2.split("'hotelcode' : '")[1].split("'")[0]
                if '"hotels-common-details' in line2:
                    next(lines)
                    next(lines)
                    g = next(lines)
                    if "<li>" in g:
                        g = next(lines)
                    g = g.replace("\r", "").replace("\t", "").replace("\n", "").strip()
                    g = g.replace("Boston,Mass", "Boston - Mass")
                    g = g.replace("Stars, Cal", "Stars, Los Angeles - Cal")
                    g = g.replace("181,", "181")
                    g = g.replace("Strand, London", "Strand, London - London")
                    g = g.replace("Scotland", "Scotland - Scotland")
                    add = g.split(",")[0]
                    g = g.replace(",Massac", "- Massac")
                    city = g.split(",")[1].strip().split(" - ")[0]
                    try:
                        state = g.split(",")[1].strip().split(" - ")[1]
                    except:
                        state = "<MISSING>"
                    if "United States" in g:
                        zc = g.rsplit(",", 1)[0].rsplit(" ", 1)[1]
                        state = state.rsplit(" ", 1)[0]
                    if "Canada" in g:
                        zc = g.split("Canada")[0].rsplit(" ", 1)[1].replace(",", "")
                    if "United Kingdom" in g:
                        zc = g.split("United Kingdom")[1].strip()
                if '"addressRegion": "' in line2:
                    city = line2.split('"addressRegion": "')[1].split('"')[0]
                if '"postalCode": "' in line2:
                    zc = line2.split('"postalCode": "')[1].split('"')[0]
                if '"streetAddress": "' in line2:
                    add = line2.split('"streetAddress": "')[1].split('"')[0]
                if 'aria-label="Phone number"' in line2:
                    phone = (
                        line2.split('aria-label="Phone number"')[1]
                        .split(">")[1]
                        .split("<")[0]
                    )
                if 'Latitude" value="' in line2:
                    lat = line2.split('Latitude" value="')[1].split('"')[0]
                if 'Longitude" value="' in line2:
                    lng = line2.split('Longitude" value="')[1].split('"')[0]
            if " Est" in zc:
                zc = zc.split(" Est")[0].strip()
            if "900 Canada Place" in add:
                zc = "V6C 3L5"
            if "900 West Georgia Street" in add:
                zc = "V6C 2W6"
            if "1038 Canada Place" in add:
                zc = "V6C 0B9"
            if " Estab" in state:
                state = state.split(" Estab")[0]
            if (
                "Alberta" in state
                or "Ontario" in state
                or "Quebec" in state
                or "Scotland" in state
                or "London" in state
                or "Manitoba" in state
            ):
                zc = state.split(" ", 1)[1]
                state = state.split(" ")[0]
            if "British Columbia" in state:
                zc = state.split("Columbia")[1].strip()
                state = "British Columbia"
            if lat == "":
                lat = "<MISSING>"
            if lng == "":
                lng = "<MISSING>"
            if "windsor-park" in loc:
                zc = "TW20 0YL"
            if "com/san-diego" in loc:
                phone = "858-314-2000"
                lng = "-117.198173"
                lat = "32.939137"
                store = "GDM"
                name = "Fairmont Grand Del Mar"
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
        except:
            pass
    for loc in intllocs:
        try:
            purl = loc
            logger.info(purl)
            name = ""
            add = ""
            city = ""
            state = ""
            zc = ""
            store = ""
            phone = ""
            lat = ""
            lng = ""
            hours = "<MISSING>"
            r2 = session.get(purl, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if "'hotelname' : '" in line2:
                    name = line2.split("'hotelname' : '")[1].split("'")[0]
                if "'hotelcode' : '" in line2:
                    store = line2.split("'hotelcode' : '")[1].split("'")[0]
                if "'hotelcountry' : '" in line2:
                    country = line2.split("'hotelcountry' : '")[1].split("'")[0]
                if '"hotels-common-details' in line2:
                    next(lines)
                    next(lines)
                    g = next(lines)
                    if "<li>" in g:
                        g = next(lines)
                    g = g.replace("\r", "").replace("\t", "").replace("\n", "")
                    raw_address = g.strip()
                    formatted_addr = parse_address_intl(raw_address)
                    add = formatted_addr.street_address_1
                    if formatted_addr.street_address_2:
                        add = add + ", " + formatted_addr.street_address_2
                    city = formatted_addr.city
                    state = (
                        formatted_addr.state if formatted_addr.state else "<MISSING>"
                    )
                    zc = (
                        formatted_addr.postcode
                        if formatted_addr.postcode
                        else "<MISSING>"
                    )
                if 'aria-label="Phone number"' in line2:
                    phone = (
                        line2.split('aria-label="Phone number"')[1]
                        .split(">")[1]
                        .split("<")[0]
                        .replace("%20", " ")
                    )
                if 'Latitude" value="' in line2:
                    lat = line2.split('Latitude" value="')[1].split('"')[0]
                if 'Longitude" value="' in line2:
                    lng = line2.split('Longitude" value="')[1].split('"')[0]
                if ',"latt":"' in line2:
                    lat = line2.split(',"latt":"')[1].split('"')[0]
                    lng = line2.split('"long":"')[1].split('"')[0]
            if lat == "":
                lat = "<MISSING>"
            if lng == "":
                lng = "<MISSING>"
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
