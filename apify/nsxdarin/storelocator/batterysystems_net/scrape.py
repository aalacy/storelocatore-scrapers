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

logger = SgLogSetup().get_logger("batterysystems_net")


def fetch_data():
    url = "https://www.batterysystems.net/pointofsale"
    r = session.get(url, headers=headers)
    website = "batterysystems.net"
    typ = "<MISSING>"
    country = "US"
    locinfo = []
    alllocs = []
    loc = "<MISSING>"
    store = "<MISSING>"
    lat = "<MISSING>"
    lng = "<MISSING>"
    logger.info("Pulling Stores")
    lines = r.iter_lines()
    for line in lines:
        line = str(line.decode("utf-8"))
        if "pointofsale.places" in line:
            items = line.split('{"id":"')
            for item in items:
                if '"title":' in item:
                    iid = item.split('"')[0]
                    ilat = item.split('"lat":"')[1].split('"')[0]
                    ilng = item.split('"lng":"')[1].split('"')[0]
                    locinfo.append(iid + "|" + ilat + "|" + ilng)
        if 'MY<span style="color:black">STORE</span></p>' in line:
            store = line.split('id="')[1].split('"')[0]
            name = line.split('">')[1].split("<")[0].strip().replace("\t", "")
        if 'style="display:none">' in line:
            next(lines)
            g = next(lines)
            g = str(g.decode("utf-8"))
            add = g.split("<br")[0].strip().replace("\t", "")
            if "/>" in add:
                add = add.split("/>")[1].strip()
            g = next(lines)
            g = str(g.decode("utf-8"))
            csz = g.split("<")[0].strip().replace("  ", " ")
            if (
                "a" not in csz
                and "e" not in csz
                and "i" not in csz
                and "o" not in csz
                and "u" not in csz
            ):
                g = next(lines)
                g = str(g.decode("utf-8"))
                csz = g.split("<")[0].strip().replace("  ", " ")
            if csz.count(" ") == 2:
                city = csz.split(" ")[0]
                state = csz.split(" ")[1]
                zc = csz.split(" ")[2]
            elif csz.count(" ") == 3:
                city = csz.split(" ")[0] + " " + csz.split(" ")[1]
                state = csz.split(" ")[2]
                zc = csz.split(" ")[3]
            else:
                city = (
                    csz.split(" ")[0]
                    + " "
                    + csz.split(" ")[1]
                    + " "
                    + csz.split(" ")[2]
                )
                state = csz.split(" ")[3]
                zc = csz.split(" ")[4]
            g = next(lines)
            g = str(g.decode("utf-8"))
            try:
                phone = g.split(" ")[1]
            except:
                phone = "<MISSING>"
            g = next(lines)
            g = str(g.decode("utf-8"))
            if '="margin-top:10px"><strong>' in g:
                hours = g.split('="margin-top:10px"><strong>')[1].split("<")[0]
            else:
                hours = "<MISSING>"
            if phone == "":
                phone = "<MISSING>"
            loc = "https://www.batterysystems.net/pointofsale"
            if "Sioux Falls South" in city:
                city = "Sioux Falls"
                state = "South Dakota"
            if "Fargo North" in city:
                city = "Fargo"
                state = "North Dakota"
            if "West Caldwell New" in city:
                city = "West Caldwell"
                state = "New Jersey"
            if "Albuquerque New" in city:
                city = "Albuquerque"
                state = "New Mexico"
            if "Charlotte North" in city or "Clayton North" in city:
                city = city.replace(" North", "")
                state = "North Carolina"
            if state == "York":
                state = "New York"
                city = city.replace(" New", "")
            infotext = []
            infotext.append(website)
            infotext.append(loc)
            infotext.append(name)
            infotext.append(add)
            infotext.append(city)
            infotext.append(state)
            infotext.append(zc)
            infotext.append(country)
            infotext.append(store)
            infotext.append(phone)
            infotext.append(typ)
            infotext.append(lat)
            infotext.append(lng)
            infotext.append(hours)
            alllocs.append(infotext)
    for item in alllocs:
        for sitem in locinfo:
            if sitem.split("|")[0] == item[8]:
                item[11] = sitem.split("|")[1]
                item[12] = sitem.split("|")[2]
                yield SgRecord(
                    locator_domain=item[0],
                    page_url=item[1],
                    location_name=item[2],
                    street_address=item[3],
                    city=item[4],
                    state=item[5],
                    zip_postal=item[6],
                    country_code=item[7],
                    store_number=item[8],
                    phone=item[9],
                    location_type=item[10],
                    latitude=item[11],
                    longitude=item[12],
                    hours_of_operation=item[13],
                )


def scrape():
    results = fetch_data()
    with SgWriter(
        deduper=SgRecordDeduper(RecommendedRecordIds.StoreNumberId)
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
