from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():
    titlelist = []
    states = [
        "Alabama",
        "Alaska",
        "Arizona",
        "Arkansas",
        "California",
        "Colorado",
        "Connecticut",
        "DC",
        "Delaware",
        "Florida",
        "Georgia",
        "Hawaii",
        "Idaho",
        "Illinois",
        "Indiana",
        "Iowa",
        "Kansas",
        "Kentucky",
        "Louisiana",
        "Maine",
        "Maryland",
        "Massachusetts",
        "Michigan",
        "Minnesota",
        "Mississippi",
        "Missouri",
        "Montana",
        "Nebraska",
        "Nevada",
        "New Hampshire",
        "New Jersey",
        "New Mexico",
        "New York",
        "North Carolina",
        "North Dakota",
        "Ohio",
        "Oklahoma",
        "Oregon",
        "Pennsylvania",
        "Rhode Island",
        "South Carolina",
        "South Dakota",
        "Tennessee",
        "Texas",
        "Utah",
        "Vermont",
        "Virginia",
        "Washington",
        "West Virginia",
        "Wisconsin",
        "Wyoming",
    ]
    for st in states:
        url = (
            "https://liveapi.yext.com/v2/accounts/me/entities/geosearch?radius=500&location="
            + st
            + "&limit=21&api_key=517cae0628fdb6c71839280b8b3d36c0&v=20181201&resolvePlaceholders=true"
        )
        divlist = session.get(url, headers=headers, verify=False).json()["response"][
            "entities"
        ]
        for div in divlist:

            street = div["address"]["line1"]
            try:
                street = street + " " + str(div["address"]["line2"])
            except:
                pass
            city = div["address"]["city"]
            state = div["address"]["region"]
            pcode = div["address"]["postalCode"]
            hourslist = div["hours"]
            hours = ""
            for hr in hourslist:
                day = hr
                try:
                    start = hourslist[hr]["openIntervals"][0]["start"] + " AM - "
                except:
                    hours = "Closed"
                    break
                endstr = hourslist[hr]["openIntervals"][0]["end"]
                end = int(endstr.split(":", 1)[0])
                if end > 12:
                    end = end - 12
                hours = (
                    hours
                    + day
                    + " "
                    + start
                    + str(end)
                    + ":"
                    + endstr.split(":", 1)[1]
                    + " PM "
                )
            if len(hours) < 3:
                hours = "<MISSING>"
            lat = div["yextDisplayCoordinate"]["latitude"]
            longt = div["yextDisplayCoordinate"]["longitude"]
            try:
                phone = div["localPhone"]
            except:
                phone = div["mainPhone"]
            phone = phone.replace("+1", "")
            phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:10]
            try:
                link = div["websiteUrl"]["url"]
            except:
                link = "<MISSING>"
            title = "CoreLife Eatery"
            if street in titlelist:
                continue
            titlelist.append(street)
            yield SgRecord(
                locator_domain="https://www.corelifeeatery.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code="US",
                store_number="<MISSING>",
                phone=phone.strip(),
                location_type="<MISSING>",
                latitude=lat,
                longitude=longt,
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
