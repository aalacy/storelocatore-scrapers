from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("crowneplaza_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    states = []
    cities = []
    locs = ["https://www.ihg.com/crowneplaza/hotels/gb/en/hobart/hbaho/hoteldetail"]
    url_home = "https://www.ihg.com/destinations/us/en/explore"
    r = session.get(url_home, headers=headers)
    Found = False
    for line in r.iter_lines():
        if '-hotels"><span>' in line:
            if (
                'href="https://www.ihg.com/destinations/us/en/mexico/' in line
                or 'href="https://www.ihg.com/destinations/us/en/canada/' in line
                or 'href="https://www.ihg.com/destinations/us/en/united-states/' in line
            ):
                lurl = line.split('href="')[1].split('"')[0]
                if lurl not in states:
                    states.append(lurl)
        if 'algeria-hotels">' in line:
            Found = True
        if (
            Found
            and '-hotels"><span>' in line
            and "united-states/" not in line
            and "/mexico/" not in line
            and "/canada/" not in line
        ):
            lurl = line.split('href="')[1].split('"')[0]
            if lurl not in states:
                states.append(lurl)
    for url in states:
        try:
            logger.info(url)
            r = session.get(url, headers=headers)
            lines = r.iter_lines()
            for line in lines:
                if '<li class="listingItem"><a' in line:
                    g = next(lines)
                    if 'href="' not in g:
                        g = next(lines)
                        g = str(g.decode("utf-8"))
                    curl = g.split('href="')[1].split('"')[0]
                    if curl not in cities:
                        cities.append(curl)
                if '"@type":"Hotel","' in line:
                    curl = (
                        line.split('"@type":"Hotel","')[1]
                        .split('"url":"')[1]
                        .split('"')[0]
                    )
                    if curl not in locs:
                        if "crowneplaza" in curl:
                            locs.append(curl)
        except:
            pass
    for url in cities:
        try:
            logger.info(url)
            r = session.get(url, headers=headers)
            lines = r.iter_lines()
            for line in lines:
                if '"@type":"Hotel","' in line:
                    curl = (
                        line.split('"@type":"Hotel","')[1]
                        .split('"url":"')[1]
                        .split('"')[0]
                    )
                    if curl not in locs:
                        if "crowneplaza" in curl:
                            locs.append(curl)
        except:
            pass

    logger.info(len(locs))
    for loc in locs:
        try:
            logger.info(loc)
            r2 = session.get(loc, headers=headers)
            website = "crowneplaza.com"
            name = ""
            city = ""
            state = ""
            country = ""
            add = ""
            zc = ""
            typ = "Hotel"
            phone = ""
            hours = "<MISSING>"
            lat = ""
            lng = ""
            store = loc.split("/hoteldetail")[0].rsplit("/", 1)[1]
            for line2 in r2.iter_lines():
                if 'property="og:title" content="' in line2 and name == "":
                    name = line2.split('property="og:title" content="')[1].split('"')[0]
                if '"name" : "' in line2 and name == "":
                    name = line2.split('"name" : "')[1].split('"')[0]
                if "|</a>" in line2:
                    rawadd = (
                        line2.split("|</a>")[0]
                        .strip()
                        .replace("\t", "")
                        .replace(" |", "|")
                        .replace("| ", "|")
                    )
                    rawadd = rawadd.replace("  ", " ")
                if 'place:location:latitude"' in line2:
                    lat = (
                        line2.split('place:location:latitude"')[1]
                        .split('content="')[1]
                        .split('"')[0]
                    )
                if 'place:location:longitude"' in line2:
                    lng = (
                        line2.split('place:location:longitude"')[1]
                        .split('content="')[1]
                        .split('"')[0]
                    )
                if '<a href="tel:' in line2:
                    phone = line2.split('<a href="tel:')[1].split('"')[0]
            if "null" in phone:
                phone = "<MISSING>"
            if state == "":
                state = "<MISSING>"
            if rawadd.count("|") == 2:
                add = rawadd.split("|")[0].split(",")[0].strip()
                city = rawadd.split("|")[0].rsplit(",", 1)[1].strip()
                state = "<MISSING>"
                zc = rawadd.split("|")[1].strip()
                country = rawadd.split("|")[2].strip()
            if rawadd.count("|") == 3:
                add = rawadd.split("|")[0].split(",")[0].strip()
                city = rawadd.split("|")[0].rsplit(",", 1)[1].strip()
                state = rawadd.split("|")[1].strip()
                zc = rawadd.split("|")[2].strip()
                country = rawadd.split("|")[3].strip()
            state = state.replace("&nbsp;", "")
            city = city.replace("&nbsp;", "")
            if zc == "":
                zc = "<MISSING>"
            if "PO Box" in city:
                add = add + " " + city
                add = add.strip()
                city = "<MISSING>"
            if " Hotels" not in name and name != "":
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
        except:
            pass


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
