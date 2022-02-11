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

logger = SgLogSetup().get_logger("trinity-health_org")


def fetch_data():
    for x in range(0, 500):
        logger.info(x)
        loc = (
            "https://www.trinity-health.org/find-a-location/location-results?page="
            + str(x)
            + "&count=9"
        )
        r = session.get(loc, headers=headers)
        for line in r.iter_lines():
            if '"Title\\":\\"' in line:
                items = line.split('"Title\\":\\"')
                for item in items:
                    if '"LocationNumber' in item:
                        country = "US"
                        typ = "<MISSING>"
                        website = "trinity-health.org"
                        phone = item.split('LocationPhoneNum\\":\\"')[1].split("\\")[0]
                        hours = "<MISSING>"
                        add = "<MISSING>"
                        city = "<MISSING>"
                        state = "<MISSING>"
                        zc = "<MISSING>"
                        name = item.split('\\"')[0]
                        loc = (
                            "https://www.trinity-health.org/"
                            + item.split('DirectUrl\\":\\"')[1].split('\\"')[0]
                        )
                        store = loc.rsplit("Id=", 1)[1]
                        try:
                            lat = item.split('"Latitude\\":\\"')[1].split("\\")[0]
                            lng = item.split('"Longitude\\":\\"')[1].split("\\")[0]
                        except:
                            lat = "<MISSING>"
                            lng = "<MISSING>"
                        addinfo = item.split('LocationAddress\\":\\"')[1].split('\\"')[
                            0
                        ]
                        if addinfo.count(",") == 3:
                            add = addinfo.split(",")[0] + " " + addinfo.split(",")[1]
                            city = addinfo.split(",")[2].strip()
                            state = addinfo.split(",")[3].strip().rsplit(" ", 1)[0]
                            try:
                                zc = addinfo.split(",")[3].strip().rsplit(" ", 1)[1]
                            except:
                                zc = "<MISSING>"
                        else:
                            add = addinfo.split(",")[0]
                            city = addinfo.split(",")[1].strip()
                            state = addinfo.split(",")[2].strip().rsplit(" ", 1)[0]
                            try:
                                zc = addinfo.split(",")[2].strip().rsplit(" ", 1)[1]
                            except:
                                zc = "<MISSING>"
                        if phone == "":
                            phone = "<MISSING>"
                        add = add.strip()
                        city = city.strip()
                        state = state.strip()
                        zc = zc.strip()
                        if add == "":
                            add = "<MISSING>"
                        if city == "":
                            city = "<MISSING>"
                        if state == "":
                            state = "<MISSING>"
                        if zc == "":
                            zc = "<MISSING>"
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
