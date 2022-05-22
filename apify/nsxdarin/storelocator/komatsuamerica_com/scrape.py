from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds

session = SgRequests()
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():
    url = "https://www.komatsu.com/api/getlocations?latitude=44.9951298&longitude=-93.4352207&radius=10000&language=en"
    r = session.get(url, headers=headers)
    if r.encoding is None:
        r.encoding = "utf-8"
    website = "komatsuamerica.com"
    for line in r.iter_lines(decode_unicode=True):
        if '"City":"' in line:
            items = line.split('"City":"')
            for item in items:
                if '"PhoneNumber":"' in item:
                    name = item.split('"CompanyName":"')[1].split('"')[0].strip()
                    phone = item.split('"PhoneNumber":"')[1].split('"')[0].strip()
                    try:
                        loc = item.split('"Website":"')[1].split('"')[0].strip()
                    except:
                        loc = "<MISSING>"
                    if loc == "":
                        loc = "<MISSING>"
                    lng = (
                        item.split('"Longitude":')[1]
                        .split(",")[0]
                        .strip()
                        .replace("}", "")
                    )
                    lat = (
                        item.split('"Latitude":')[1]
                        .split(",")[0]
                        .strip()
                        .replace("}", "")
                    )
                    add = item.split('"Address":"')[1].split('"')[0].strip()
                    try:
                        typ = (
                            item.split('"EquipmentTypes":[')[1]
                            .strip()
                            .split("]")[0]
                            .replace('"', "")
                        )
                    except:
                        typ = "<MISSING>"
                    try:
                        state = item.split('"State":"')[1].split('"')[0].strip()
                    except:
                        state = "<MISSING>"
                    city = item.split('"')[0].strip()
                    zc = item.split('"Zip":"')[1].split('"')[0].strip()
                    store = "<MISSING>"
                    country = "US"
                    hours = "<MISSING>"
                    if " " in zc:
                        country = "CA"
                    if state == "" or city == "" or state == "XX":
                        pass
                    else:
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
