from lxml import html
from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgpostal.sgpostal import parse_address_intl

logger = SgLogSetup().get_logger("freightliner_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    uscan = [
        "https://freightliner.com/dealer-search/countries/CANADA",
        "https://freightliner.com/dealer-search/countries/UNITED-STATES",
    ]
    locs = []
    for url in uscan:
        r = session.get(url, headers=headers)
        for line in r.iter_lines():
            if '<a href="https://freightliner.com/dealers/' in line:
                locs.append(line.split('href="')[1].split('"')[0])
    website = "freightliner.com"
    typ = "<MISSING>"
    lat = "<MISSING>"
    hours = "<MISSING>"
    lng = "<MISSING>"
    url = "https://freightliner.com/dealer-search/countries"
    r = session.get(url, headers=headers)
    for line in r.iter_lines():
        if '<a href="https://freightliner.com/dealers/' in line:
            locs.append(line.split('href="')[1].split('"')[0])
    for loc in locs:
        logger.info(loc)
        lurl = "<MISSING>"
        country = loc.split("dealers/")[1].split("/")[0]
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if "<h2>" in line:
                phone = ""
                rawadd = ""
                city = ""
                state = ""
                zc = ""
                add = ""
                if "<a href" in line:
                    name = line.split('">')[1].split("<")[0]
                    lurl = (
                        "https://freightliner.com"
                        + line.split('a href="')[1].split('"')[0]
                    )
                    lurl = lurl.split("&amp")[0]
                else:
                    name = line.split("<h2>")[1].split("<")[0]
            if '<a class="phone" href="tel:' in line:
                phone = line.split('<a class="phone" href="tel:')[1].split('"')[0]
            if '<h3 class="icon-map-pin">' in line:
                rawadd = (
                    line.split('<h3 class="icon-map-pin">')[1]
                    .split("</h3>")[0]
                    .replace("<br>", "")
                    .replace("  ", " ")
                    .strip()
                )
                formatted_addr = parse_address_intl(rawadd)
                add = formatted_addr.street_address_1
                if formatted_addr.street_address_2:
                    add = add + ", " + formatted_addr.street_address_2
                city = formatted_addr.city
                state = formatted_addr.state if formatted_addr.state else "<MISSING>"
                zc = formatted_addr.postcode if formatted_addr.postcode else "<MISSING>"
                if lurl != "<MISSING>":
                    r2 = session.get(lurl, headers=headers)
                    tree = html.fromstring(r2.text)
                    typs = tree.xpath("//h4//text()")
                    typs = list(filter(None, [c.strip() for c in typs]))
                    typ = ", ".join(typs) or "<MISSING>"
                    days = 0
                    hours = ""
                    lines = r2.iter_lines()
                    for line2 in lines:
                        if '"addressLocality": "' in line2:
                            city = line2.split('"addressLocality": "')[1].split('"')[0]
                        if '"addressRegion": "' in line2:
                            state = line2.split('"addressRegion": "')[1].split('"')[0]
                        if '"streetAddress": "' in line2:
                            add = line2.split('"streetAddress": "')[1].split('"')[0]
                        if '"telephone": "' in line2:
                            phone = line2.split('"telephone": "')[1].split('"')[0]
                        if "day:</header>" in line2:
                            days = days + 1
                            if days <= 7:
                                hrs = (
                                    line2.split("<header>")[1].split("<")[0].strip()
                                    + ": "
                                )
                                hrs = (
                                    hrs
                                    + next(lines)
                                    .split("<div>")[1]
                                    .split("<")[0]
                                    .strip()
                                )
                                if hours == "":
                                    hours = hrs
                                else:
                                    hours = hours + "; " + hrs
                    rawadd = add + " " + city + " " + state
                if hours == "":
                    hours = "<MISSING>"
                try:
                    add = add.replace("&#39;", "'").replace("&amp;", "&")
                except:
                    add = "<MISSING>"
                try:
                    name = name.replace("&#39;", "'").replace("&amp;", "&")
                except:
                    name = "<MISSING>"
                if country == "CANADA":
                    country = "CA"
                if country == "UNITED STATES":
                    country = "US"
                hours = hours.replace("::", ":")
                if "," in phone:
                    phone = phone.split(",")[0].strip()
                if "y" in phone:
                    phone = phone.split("y")[0].strip()
                if " /" in phone:
                    phone = phone.split(" /")[0].strip()
                if "a" in phone:
                    phone = phone.split("a")[0].strip()
                try:
                    if "9" in city:
                        city = "<MISSING>"
                except:
                    pass
                try:
                    if "No." in city:
                        city = "<MISSING>"
                except:
                    pass
                try:
                    if "Km" in city:
                        city = "<MISSING>"
                except:
                    pass
                rawadd = rawadd.replace("&#39;", "'")
                try:
                    city = city.replace("&#39;", "'")
                except:
                    city = "<MISSING>"
                name = (
                    name.replace("&#243;", "o")
                    .replace("&#250;", "u")
                    .replace("&#225;", "a")
                    .replace("&#233;", "e")
                )
                try:
                    store = str(lurl).split("code=")[1].split("&")[0].strip()
                except:
                    store = "<MISSING>"

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
                    raw_address=rawadd,
                    hours_of_operation=hours,
                )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.PhoneNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
