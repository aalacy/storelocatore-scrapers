from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import SgRecordID

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

logger = SgLogSetup().get_logger("mayoclinichealthsystem_org")


def fetch_data():
    locs = []
    url = "https://www.mayoclinichealthsystem.org/HealthSystemInternet/LocationAddress/GetLocationMapRailResults?page=1&pageSize=100&sourceLat=44.02209&sourceLong=-92.46997&activeSite=hsinternet"
    r = session.get(url, headers=headers)
    website = "mayoclinichealthsystem.org"
    typ = "<MISSING>"
    country = "US"
    logger.info("Pulling Stores")
    for line in r.iter_lines():
        line = str(line.decode("utf-8"))
        if 'href="/locations/' in line:
            locs.append(
                "https://www.mayoclinichealthsystem.org"
                + line.split('href="')[1].split('"')[0]
            )
    for loc in locs:
        logger.info(loc)
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
        r2 = session.get(loc, headers=headers)
        for line2 in r2.iter_lines():
            line2 = str(line2.decode("utf-8"))
            if '<h5 class="list-item-name">' in line2 and "</h5>" in line2:
                if add != "":
                    if phone == "":
                        phone = "<MISSING>"
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
                add = ""
                city = ""
                state = ""
                zc = ""
                hours = ""
                phone = ""
                typ = line2.split('<h5 class="list-item-name">')[1].split("<")[0]
            if '<address class="list-item-address">' in line2 and add == "":
                addinfo = line2.split('<address class="list-item-address">')[1].split(
                    "<"
                )[0]
                if addinfo.count(",") == 2:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    city = line2.split(",")[1].strip()
                    state = line2.split(",")[2].strip().split(" ")[0]
                    name = city + ", " + state
                    zc = line2.split(",")[2].strip().split(" ")[1].split("<")[0]
                elif addinfo.count(",") == 3:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    add = add + " " + line2.split(",")[1].strip()
                    city = line2.split(",")[2].strip()
                    state = line2.split(",")[3].strip().split(" ")[0]
                    zc = line2.split(",")[3].strip().split(" ")[1].split("<")[0]
                else:
                    add = line2.split('<address class="list-item-address">')[1].split(
                        ","
                    )[0]
                    add = add + " " + line2.split(",")[1].strip()
                    add = add + " " + line2.split(",")[2].strip()
                    city = line2.split(",")[3].strip()
                    state = line2.split(",")[4].strip().split(" ")[0]
                    zc = line2.split(",")[4].strip().split(" ")[1].split("<")[0]
            if "href='tel://" in line2:
                phone = line2.split("href='tel://")[1].split("'")[0]
            if "Hours:</li><li><span>" in line2:
                hours = line2.split("Hours:</li><li><span>")[1].split("</ul>")[0]
                hours = (
                    hours.replace("</span>", ": ")
                    .replace("</li><li><span>", "; ")
                    .replace("</li>", "")
                )
                hours = hours.replace("::", ":")
                if "<li>" in hours:
                    hours = hours.split("<li>")[0].strip()
            if "</html>" in line2:
                if add != "":
                    if phone == "":
                        phone = "<MISSING>"
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
    with SgWriter(
        deduper=SgRecordDeduper(SgRecordID({SgRecord.Headers.STREET_ADDRESS}))
    ) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
