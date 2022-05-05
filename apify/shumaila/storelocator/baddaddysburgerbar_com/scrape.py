from datetime import timedelta
from datetime import date
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

session = SgRequests()
headers = {
    "authority": "api.dineengine.io",
    "method": "GET",
    "path": "/baddaddys/custom/dineengine/vendor/olo/restaurants/near?lat=35.262082&long=-81.18730049999999&radius=25&limit=10&calendarstart=20220301&calendarend=20220308",
    "scheme": "https",
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "content-type": "application/json",
    "origin": "https://baddaddysburgerbar.com",
    "referer": "https://baddaddysburgerbar.com/",
    "sec-ch-ua": '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": '"Windows"',
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "cross-site",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "x-device-id": "ce7713f7-4eea-452d-beca-84922d992c25",
}


def fetch_data():
    linklist = []
    EndDate = date.today() + timedelta(days=6)
    mylist = static_coordinate_list(40, SearchableCountries.USA)
    for lat, lng in mylist:
        url = (
            "https://api.dineengine.io/baddaddys/custom/dineengine/vendor/olo/restaurants/near?lat="
            + str(lat)
            + "&long="
            + str(lng)
            + "&radius=1000&limit=100&calendarstart="
            + str(date.today()).replace("-", "")
            + "&calendarend="
            + str(EndDate).replace("-", "")
        )

        try:
            loclist = session.get(url, headers=headers).json()["restaurants"]
        except:
            continue
        for loc in loclist:
            store = loc["id"]
            title = loc["name"]
            street = loc["streetaddress"]
            phone = loc["telephone"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["zip"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            link = "https://baddaddysburgerbar.com/locations/" + loc["slug"]
            if link in linklist:
                continue
            linklist.append(link)

            hrslist = loc["calendars"][0]["ranges"]
            hours = ""
            for hr in hrslist:
                day = hr["weekday"]
                strtime = hr["start"].split(" ", 1)[-1] + " AM - "
                endt = int(hr["end"].split(" ", 1)[-1].split(":", 1)[0])
                if endt > 12:
                    endt = endt - 12
                hours = (
                    hours
                    + day
                    + " "
                    + strtime
                    + str(endt)
                    + ":"
                    + hr["end"].split(" ", 1)[-1].split(":", 1)[1]
                    + " PM "
                )
            yield SgRecord(
                locator_domain="https://baddaddysburgerbar.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode,
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
