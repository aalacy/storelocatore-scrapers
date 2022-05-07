from sgrequests import SgRequests
from sglogging import SgLogSetup
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

logger = SgLogSetup().get_logger("deli-delicious_com")

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://viewer.blipstar.com/searchdbnew?uid=2070622&lat=45.00580&lng=-93.41930&type=nearest&value=5000&keyword=&sp=&son=&product=&product2=&cnt=us&mb=false&state=&r=0.536340923462526"
    r = session.get(url, headers=headers)
    website = "deli-delicious.com"
    typ = "<MISSING>"
    country = "US"
    loc = "<MISSING>"
    for line in r.iter_lines():
        if '{"n":"' in line:
            items = line.split('{"n":"')
            for item in items:
                if '"s":"' in item:
                    name = item.split('"')[0]
                    state = item.split('"s":"')[1].split('"')[0]
                    add = item.split('"ad":"')[1].split('"')[0].split(",")[0].strip()
                    city = (
                        item.split('"a":"')[1]
                        .split("<span class='storecity'>")[1]
                        .split("<")[0]
                    )
                    zc = item.split('"pc":"')[1].split('"')[0]
                    try:
                        phone = item.split('"p":"')[1].split('"')[0]
                    except:
                        phone = ""
                    try:
                        loc = (
                            item.split('"w":"')[1]
                            .split('"')[0]
                            .replace("\\", "")
                            .replace("#s:search.php,menu.php", "")
                            .split("#s:")[0]
                            .strip()
                        )
                    except:
                        loc = "<MISSING>"
                    store = item.split('"bpid":')[1].split(",")[0]
                    lat = item.split('"lat":"')[1].split('"')[0]
                    lng = item.split('"lng":"')[1].split('"')[0]
                    try:
                        hours = "Mon: " + item.split('"mon":"')[1].split('"')[0]
                        hours = (
                            hours + "; Tue: " + item.split('"tue":"')[1].split('"')[0]
                        )
                        hours = (
                            hours + "; Wed: " + item.split('"wed":"')[1].split('"')[0]
                        )
                        hours = (
                            hours + "; Thu: " + item.split('"thu":"')[1].split('"')[0]
                        )
                        hours = (
                            hours + "; Fri: " + item.split('"fri":"')[1].split('"')[0]
                        )
                        hours = (
                            hours + "; Sat: " + item.split('"sat":"')[1].split('"')[0]
                        )
                        hours = (
                            hours + "; Sun: " + item.split('"sun":"')[1].split('"')[0]
                        )
                    except:
                        hours = "<MISSING>"
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
    with SgWriter(deduper=SgRecordDeduper(RecommendedRecordIds.GeoSpatialId)) as writer:
        for rec in results:
            writer.write_row(rec)


scrape()
