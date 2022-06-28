import json
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list
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

    mylist = static_coordinate_list(100, SearchableCountries.USA)

    mylist = mylist + [
        ("38.895", "-77.03667"),
        ("-117.2119253", "32.737944"),
        ("-117.691168", "33.465728"),
    ]

    linklist = []
    for latnow, lngnow in mylist:
        url = (
            "https://fitnesstogether.com/locator?q=United%20States&lat="
            + str(latnow)
            + "&lng="
            + str(lngnow)
            + "&limit=25"
        )

        try:
            loclist = session.get(url, headers=headers).json()["locations"]
        except:
            continue
        for loc in loclist:

            if loc["status"] == "soon":
                continue
            title = loc["name"]
            store = loc["id"]
            link = "https://fitnesstogether.com/" + loc["slug"]
            if link in linklist:
                continue
            linklist.append(link)
            street = loc["address"] + " " + loc["address_2"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip_code"]
            phone = loc["phone_number"]
            if len(phone) < 3:
                phone = "<MISSING>"
            lat = loc["latitude"]
            longt = loc["longitude"]
            hourslist = json.loads(loc["business_hours"])
            hours = ""
            for hr in hourslist:
                day = hr
                hr = hourslist[day]
                start = ":".join(hr["start"].split(":")[0:2])
                end = hr["end"].split(":")[0:2]
                endtime = (int)(end[0])
                if endtime > 12:
                    endtime = endtime - 12
                hours = (
                    hours
                    + day
                    + " "
                    + start
                    + " AM - "
                    + str(endtime)
                    + ":"
                    + end[1]
                    + " PM "
                )
            yield SgRecord(
                locator_domain="https://fitnesstogether.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
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
