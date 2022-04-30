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

    url = "https://idealmarket.us/store-locator/"
    r = session.get(url, headers=headers)
    loclist = r.text.split('"places":', 1)[1].split(',"map_tabs":', 1)[0]
    loclist = json.loads(loclist)
    for loc in loclist:

        title = loc["title"]
        store = title.split("#", 1)[1]
        street = loc["address"]
        lat = loc["location"]["lat"]
        longt = loc["location"]["lng"]
        city = loc["location"]["city"]
        state = loc["location"]["state"]
        pcode = loc["location"]["postal_code"]
        street = street.split(", " + state, 1)[0]
        phone = loc["location"]["extra_fields"]["phone"]
        if ", " + city in street:
            street = street.split(", " + city, 1)[0]
        elif " " + city in street:
            street = street.split(" " + city, 1)[0]
        ltypelist = loc["categories"]
        ltype = ""
        for lt in ltypelist:
            ltype = ltype + lt["name"] + ", "
        ltype = ltype[0 : len(ltype) - 2]

        yield SgRecord(
            locator_domain="https://idealmarket.us/",
            page_url=url,
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
            hours_of_operation="<MISSING>",
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.StoreNumberId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
