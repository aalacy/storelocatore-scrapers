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

    url = "https://api.storerocket.io/api/user/3MZpoQ2JDN/locations?radius=250&units=miles"
    loclist = session.get(url, headers=headers, verify=False).json()["results"][
        "locations"
    ]
    for loc in loclist:
        title = loc["name"]
        store = loc["id"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["address_line_1"]
        try:
            city = loc["city"].strip()
            state = loc["state"]
            pcode = loc["postcode"]
        except:
            street, city, state, pcode = loc["address"].split(", ")
        link = str(loc["url"])
        if len(link) < 6:
            link = "<MISSING>"
        ccode = "US"
        if str(street) == "None":
            street, city, state, pcode = loc["address"].split(", ")
        phone = (
            loc["phone"]
            .replace("(", "")
            .replace(")", "")
            .replace("-", "")
            .replace(" ", "")
        )
        phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        if "Indiana" in state:
            state = "IN"
        elif "Illinois" in state:
            state = "IL"
        yield SgRecord(
            locator_domain="https://theoriginalpizzaking.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode,
            country_code=ccode,
            store_number=store,
            phone=phone.strip(),
            location_type="<MISSING>",
            latitude=lat,
            longitude=longt,
            hours_of_operation="<MISSING>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.GeoSpatialId)
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
