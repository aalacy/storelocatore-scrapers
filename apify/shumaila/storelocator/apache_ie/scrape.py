from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "x-requested-with": "XMLHttpRequest",
}


def fetch_data():

    url = "https://www.apache.ie/General/GetFilteredStores/"
    dataobj = {"includeSliceStores": "true", "storeIds": ""}
    loclist = session.post(url, data=dataobj, headers=headers).json()
    for loc in loclist:

        store = loc["store_id"]
        title = loc["name"]
        lat = loc["latitude"]
        longt = loc["longitude"]
        street = loc["address_line_1"]
        city = loc["address_line_2"].encode("ascii", "ignore").decode("ascii")
        try:
            pcode, city = city.split(" County", 1)
            city = "County " + city
        except:
            pcode, city = city.split(" Co ", 1)
            city = "Co " + city
        if (
            len(pcode.strip().split(" ", 1)[0]) == 3
            and len(pcode.strip().split(" ", 1)[1]) == 4
        ) or len(pcode.strip()) == 7:
            if "Co " in pcode:
                city = pcode + " " + city
                pcode = "<MISSING>"
        else:
            city = pcode + " " + city
            pcode = "<MISSING>"
        if " Clane" in city:
            pcode, city = city.split("Clane", 1)
            city = "Clane " + city
        hourslist = loc["opening_hours"]
        hours = ""
        for hr in hourslist:
            hours = hours + hr["key"] + " " + hr["value"] + " "
        phone = loc["phone_number"]
        link = "https://www.apache.ie" + loc["details_url"]
        state = city
        city = title

        yield SgRecord(
            locator_domain="https://www.apache.ie",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state,
            zip_postal=pcode.strip(),
            country_code="IE",
            store_number=str(store),
            phone=phone.strip(),
            location_type=SgRecord.MISSING,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(record_id=RecommendedRecordIds.PageUrlId)
    ) as writer:

        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
