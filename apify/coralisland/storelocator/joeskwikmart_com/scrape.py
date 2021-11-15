import re
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import sglog

DOMAIN = "joeskwikmart.com"
BASE_URL = "https://joeskwikmart.com/"
API_URL = "https://joeskwikmart.com/locations?radius=-1&filter_catid=0&limit=0&filter_order=distance&searchzip=Pennsylvania"
log = sglog.SgLogSetup().get_logger(logger_name=DOMAIN)
session = SgRequests()

headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
}


def fetch_data(sgw: SgWriter):
    cleanr = re.compile(r"<[^>]+>")
    mydata = {
        "searchzip": "You",
        "task": "search",
        "radius": "-1",
        "limit": "0",
        "option": "com_mymaplocations",
        "component": "com_mymaplocations",
        "Itemid": "223",
        "zoom": "9",
        "limitstart": "0",
        "format": "json",
        "geo": "1",
        "latitude": "37.09024",
        "longitude": "-95.712891",
    }

    loclist = session.post(API_URL, data=mydata, headers=headers).json()["features"]
    for loc in loclist:
        longt = loc["geometry"]["coordinates"][0]
        lat = loc["geometry"]["coordinates"][1]
        title = loc["properties"]["name"]
        link = BASE_URL + loc["properties"]["url"]
        content = loc["properties"]["fulladdress"]
        check_phone = re.search(r"tel:(\d+)", content)
        if not check_phone:
            phone = "<MISSING>"
        else:
            phone = check_phone.group(1)
        content = re.sub(cleanr, "\n", str(content)).strip().splitlines()
        street = content[0]
        city, state = content[1].split("&#44;", 1)
        pcode = content[2].split("&nbsp;", 1)[1]
        store = title.split("#")[1]
        title = title.replace("&apos;", "'")
        hours = "<MISSING>"
        log.info("Append {} => {}".format(title, street))
        sgw.write_row(
            SgRecord(
                locator_domain=DOMAIN,
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code="US",
                store_number=store,
                phone=phone,
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
                hours_of_operation=hours,
            )
        )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
