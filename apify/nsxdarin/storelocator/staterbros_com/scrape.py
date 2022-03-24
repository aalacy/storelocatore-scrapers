from sgrequests import SgRequests
from sglogging import SgLogSetup
import usaddress
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("staterbros_com")


def fetch_data():
    locs = []
    url = "https://www.staterbros.com/stores-sitemap.xml"
    r = session.get(url, headers=headers)
    website = "staterbros.com"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        if "<loc>https://www.staterbros.com/stores/" in line:
            locs.append(line.split("<loc>")[1].split("<")[0])
    for loc in locs:
        if loc != "https://www.staterbros.com/stores/":
            logger.info(loc)
            name = ""
            add = ""
            city = ""
            rawadd = ""
            state = ""
            zc = ""
            phone = ""
            lat = "<MISSING>"
            lng = "<MISSING>"
            store = loc.split("/stores/")[1].split("/")[0]
            hours = ""
            r2 = session.get(loc, headers=headers)
            lines = r2.iter_lines()
            for line2 in lines:
                if (
                    '<div class="elementor-text-editor elementor-clearfix">' in line2
                    and phone == ""
                    and rawadd != ""
                ):
                    g = next(lines)
                    ph = g.split("<")[0].strip().replace("\t", "")
                    if ph.count("-") == 2:
                        phone = ph
                    if ")" in ph and "(" in ph:
                        phone = ph
                if "<title>" in line2:
                    name = line2.split("<title>")[1].split(" - ")[0]
                if (
                    '<div class="elementor-text-editor elementor-clearfix">' in line2
                    and rawadd == ""
                ):
                    g = next(lines)
                    rawadd = g.split("<")[0].strip().replace("\t", "")
                    try:
                        add = usaddress.tag(rawadd)
                        baseadd = add[0]
                        if "AddressNumber" not in baseadd:
                            baseadd["AddressNumber"] = ""
                        if "StreetName" not in baseadd:
                            baseadd["StreetName"] = ""
                        if "StreetNamePostType" not in baseadd:
                            baseadd["StreetNamePostType"] = ""
                        if "PlaceName" not in baseadd:
                            baseadd["PlaceName"] = "<INACCESSIBLE>"
                        if "StateName" not in baseadd:
                            baseadd["StateName"] = "<INACCESSIBLE>"
                        if "ZipCode" not in baseadd:
                            baseadd["ZipCode"] = "<INACCESSIBLE>"
                        address = (
                            add[0]["AddressNumber"]
                            + " "
                            + add[0]["StreetName"]
                            + " "
                            + add[0]["StreetNamePostType"]
                        )
                        address = address.encode("ascii").decode()
                        if address == "":
                            address = "<MISSING>"
                        city = add[0]["PlaceName"]
                        state = add[0]["StateName"]
                        zc = add[0]["ZipCode"]
                    except:
                        pass
                if '<p class="elementor-icon-box-description">' in line2:
                    g = next(lines)
                    if "PM" in g:
                        hours = (
                            g.strip()
                            .split("<p>")[1]
                            .split("</p>")[0]
                            .replace("<b>", "")
                            .replace("</b>", ":")
                            .replace("&#8211;", "-")
                        )
            if add != "":
                if state == "Linda":
                    state = "CA"
                    city = "Yorba Linda"
                if phone == "":
                    phone = "<MISSING>"
                if "1717 East Vista" in rawadd:
                    add = "1717 East Vista Chino"
                    city = "Palm Springs"
                if ", L A" in city:
                    city = city.split(", L A")[0].strip()
                if "1830 E Rte 66" in rawadd:
                    add = "1830 E Rte 66"
                if "16920 State Hwy 14" in rawadd:
                    add = "16920 State Hwy 14"
                if "1850 E Ave. J" in rawadd:
                    add = "1850 E Ave. J"
                if "2845 W Ave L" in rawadd:
                    add = "2845 W Ave L"
                name = name.replace("</title>", "")
                if " | " in name:
                    name = name.split(" | ")[0]
                yield SgRecord(
                    locator_domain=website,
                    page_url=loc,
                    location_name=name,
                    street_address=address,
                    raw_address=rawadd,
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
