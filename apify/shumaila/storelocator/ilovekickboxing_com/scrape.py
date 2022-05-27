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

    url = "https://api-v3.ilovekickboxing.com/api/v1"
    dataobj = {
        "query": "query\n          {\n            locations(\n              first :500\n              active : true\n              orderBy: [{field: NAME, order: ASC}]\n              )\n            {\n              paginatorInfo {\n                total\n              }\n              data {\n                ID\n                Name\n                City\n                lat\n                lng\n                Line1\n                ZipCode\n                distance\n                phone\n                state\n                {\n                  ID\n                  Code\n                }\n                url_slug\n                phone\n                opening_day\n                opening_message\n              }\n\n            }\n          }"
    }
    loclist = session.post(url, data=dataobj, headers=headers).json()["data"][
        "locations"
    ]["data"]
    for loc in loclist:

        store = loc["ID"]
        title = loc["Name"]
        city = loc["City"]
        lat = loc["lat"]
        longt = loc["lng"]
        street = loc["Line1"]
        pcode = loc["ZipCode"]
        phone = loc["phone"].strip()
        if "-" not in phone:
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
        state = loc["state"]["Code"]
        link = "https://www.ilovekickboxing.com/" + loc["url_slug"]
        ccode = "US"
        if pcode.isdigit():
            pass
        else:
            ccode = "CA"
        yield SgRecord(
            locator_domain="https://www.ilovekickboxing.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=SgRecord.MISSING,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
