import json
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    url = "https://stockist.co/api/v1/u3959/locations/all.js?callback=_stockistAllStoresCallback"

    loclist = session.get(url, headers=headers).text
    loclist = loclist.split("_stockistAllStoresCallback(", 1)[1].split(");", 1)[0]

    loclist = json.loads(loclist)
    for loc in loclist:

        store = loc["id"]
        title = loc["name"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = loc["address_line_1"] + str(loc["address_line_2"])
        street = street.replace("None", "")
        city = loc["city"]
        try:
            state = loc["state"].strip()
        except:
            state = "<MISSING>"
        try:
            pcode = loc["postal_code"].strip()
        except:
            pcode = "<MISSING>"
        try:
            phone = loc["phone"].strip()
        except:
            phone = "<MISSING>"
        try:
            hours = loc["description"].replace("\t", " ").replace("\n", " ").strip()
        except:
            hours = "<MISSING>"
        ltype = "<MISSING>"
        if "COMING SOON" in title:
            ltype = "COMING SOON"
        yield SgRecord(
            locator_domain="https://5starnutritionusa.com/",
            page_url="https://5starnutritionusa.com/pages/store-locator",
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code="US",
            store_number=str(store),
            phone=phone.strip(),
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
