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

logger = SgLogSetup().get_logger("dominos_com___hash_storelist2")


def fetch_data():
    urls = [
        "https://www.dominos.bg/stores",
        "https://www.dominos.com.cy/stores",
        "https://www.dominos-pizza.ro/stores",
        "https://www.dominos.gr/stores",
        "https://www.dominos.mk/stores",
        "https://www.dominos.mt/stores",
        "https://www.dominospizzanc.com/stores",
    ]
    for url in urls:
        r = session.get(url, headers=headers)
        website = "dominos.com/#storelist2"
        country = url.split("/stores")[0].rsplit(".", 1)[1].upper()
        if "dominospizzanc" in url:
            country = "CY"
        locs = []
        typ = "<MISSING>"
        logger.info("Pulling Stores")
        for line in r.iter_lines():
            if "href='/menu/" in line:
                stub = line.split("href='/menu/")[1].split("'")[0]
                lurl = url + "/" + stub + ".php"
                locs.append(lurl)
        for loc in locs:
            logger.info(loc)
            r2 = session.get(loc, headers=headers)
            name = ""
            add = ""
            city = loc.split("/stores/")[1].split("-")[0].title()
            if ".Php" in city:
                city = city.replace(".Php", "")
            state = "<MISSING>"
            zc = "<MISSING>"
            phone = ""
            lat = ""
            lng = ""
            store = "<MISSING>"
            hours = ""
            for line2 in r2.iter_lines():
                if "maps.LatLng(" in line2:
                    lat = line2.split("maps.LatLng(")[1].split(",")[0].strip()
                    lng = (
                        line2.split("maps.LatLng(")[1]
                        .split(",")[1]
                        .split(")")[0]
                        .strip()
                    )
                if "<h2" in line2 and name == "":
                    name = line2.split(">")[1].split("<")[0]
                if add == "" and 'class="store-details-text">' in line2:
                    add = line2.split('class="store-details-text">')[1].split("<")[0]
                if "[name_en] => " in line2:
                    name = (
                        line2.split("[name_en] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if "[number] => " in line2:
                    add = (
                        line2.split("[number] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if "[street] => " in line2:
                    add = (
                        add
                        + " "
                        + line2.split("[street] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if "[postcode] => " in line2:
                    zc = (
                        line2.split("[postcode] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                    if zc == "":
                        zc = "<MISSING>"
                if 'href="tel:' in line2:
                    phone = line2.split('href="tel:')[1].split('"')[0]
                if "[lng] => " in line2:
                    lng = (
                        line2.split("[lng] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if "[lat] => " in line2:
                    lat = (
                        line2.split("[lat] =>")[1]
                        .strip()
                        .replace("\r", "")
                        .replace("\t", "")
                        .replace("\n", "")
                    )
                if '<span class="font-bold">' in line2:
                    hours = line2.split('<span class="font-bold">')[1].split("<")[0]
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
