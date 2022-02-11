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

    url = "https://www.campbowwow.com/locations/?CallAjax=GetLocations"
    loclist = session.get(url, headers=headers).json()

    for loc in loclist:

        link = "https://www.campbowwow.com" + loc["Path"]
        store = loc["FranchiseLocationID"]
        title = loc["FranchiseLocationName"]
        street = loc["Address1"] + loc["Address2"]
        city = loc["City"]
        state = loc["State"]
        pcode = loc["ZipCode"]
        ccode = loc["Country"]
        lat = loc["Latitude"]
        longt = loc["Longitude"]
        phone = loc["Phone"]
        if len(str(phone)) < 3:
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
        else:
            phone = "<MISSING>"
        try:
            hourslist = loc["LocationHours"]
            hourslist = (
                hourslist.replace("]", "}").replace("[", "{").replace("}{", "},{")
            )
            hourslist = "[" + hourslist + "]"
            hourslist = json.loads(hourslist)

            hours = ""
            for hr in hourslist:
                day = hr["Interval"]
                if "Holiday" in day:
                    break
                start = hr["OpenTime"]
                end = hr["CloseTime"]
                st = (int)(start.split(":", 1)[0])
                if st > 12:
                    st = st - 12
                endst = (int)(end.split(":", 1)[0])
                if endst > 12:
                    endst = endst - 12
                hours = (
                    hours
                    + day
                    + " "
                    + str(st)
                    + ":"
                    + start.split(":")[1]
                    + " AM - "
                    + str(endst)
                    + ":"
                    + end.split(":")[1]
                    + " PM "
                )
        except:

            hours = "<MISSING>"
        yield SgRecord(
            locator_domain="https://www.campbowwow.com/",
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
