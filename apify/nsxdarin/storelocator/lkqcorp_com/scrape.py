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

logger = SgLogSetup().get_logger("lkqcorp_com")


def fetch_data():
    website = "lkqcorp.com"
    typ = "<MISSING>"
    canada = [
        "QC",
        "ON",
        "NS",
        "NF",
        "NL",
        "PE",
        "PEI",
        "AB",
        "SK",
        "YT",
        "NU",
        "BC",
    ]
    usstates = [
        "AK",
        "AL",
        "AR",
        "AS",
        "AZ",
        "CA",
        "CO",
        "CT",
        "DC",
        "DE",
        "FL",
        "GA",
        "GU",
        "HI",
        "IA",
        "ID",
        "IL",
        "IN",
        "KS",
        "KY",
        "LA",
        "MA",
        "MD",
        "ME",
        "MI",
        "MN",
        "MO",
        "MP",
        "MS",
        "MT",
        "NC",
        "ND",
        "NE",
        "NH",
        "NJ",
        "NM",
        "NV",
        "NY",
        "OH",
        "OK",
        "OR",
        "PA",
        "PR",
        "RI",
        "SC",
        "SD",
        "TN",
        "TX",
        "UM",
        "UT",
        "VA",
        "VI",
        "VT",
        "WA",
        "WI",
        "WV",
        "WY",
    ]
    for x in range(1, 250):
        url = (
            "https://www.lkqcorp.com/wp-json/cf-elementor-modules/v1/location-finder/search?category_id=0&lat=&lng=&page="
            + str(x)
            + "&range=0&per_page=8"
        )
        r = session.get(url, headers=headers)
        logger.info("Pulling Stores Page %s..." % str(x))
        for line in r.iter_lines():
            if '{"post_id":"' in line:
                items = line.split('{"post_id":"')
                for item in items:
                    if "https:" in item:
                        hours = "<MISSING>"
                        lurl = (
                            item.split('"location_url":"')[1]
                            .split('"')[0]
                            .replace("\\", "")
                        )
                        store = item.split('"')[0]
                        lat = item.split('"location_latitude":"')[1].split('"')[0]
                        lng = item.split('"location_longitude":"')[1].split('"')[0]
                        name = item.split('"location_name":"')[1].split('"')[0]
                        phone = item.split('"location_phone":"')[1].split('"')[0]
                        if phone == "":
                            phone = "<MISSING>"
                        addinfo = item.split('"location_address":"')[1].split('"')[0]
                        try:
                            if addinfo.count(",") == 2:
                                add = addinfo.split(",")[0]
                                city = addinfo.split(",")[1].strip()
                                state = addinfo.split(",")[2].strip().split(" ")[0]
                                zc = addinfo.split(",")[2].strip().split(" ", 1)[1]
                            else:
                                add = (
                                    addinfo.split(",")[0]
                                    + " "
                                    + addinfo.split(",")[1].strip()
                                )
                                city = addinfo.split(",")[2].strip()
                                state = addinfo.split(",")[3].strip().split(" ")[0]
                                zc = addinfo.split(",")[3].strip().split(" ", 1)[1]
                        except:
                            pass
                        if "-" in name:
                            name = name.split("-")[0].strip()
                        country = "<MISSING>"
                        if state in canada:
                            country = "CA"
                        if state in usstates:
                            country = "US"
                        if state not in canada and state not in usstates:
                            country = addinfo.rsplit(",", 1)[1].strip()
                            state = "<MISSING>"
                            zc = "<INACCESSIBLE>"
                            add = addinfo.split(",")[0].strip()
                            city = "<INACCESSIBLE>"
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
                            raw_address=addinfo,
                            hours_of_operation=hours,
                        )


def scrape():
    results = fetch_data()
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
