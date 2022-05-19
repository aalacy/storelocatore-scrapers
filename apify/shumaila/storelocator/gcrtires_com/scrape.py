from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_coordinate_list

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest",
}


def fetch_data():

    daylist = ["mon", "tues", "wednes", "thurs", "fri", "satur", "sun"]
    mylist = static_coordinate_list(40, SearchableCountries.USA)
    storelist = []
    for lat, lng in mylist:

        url = (
            "https://www.gcrtires.com/bcsutil/commercial/locations?lat="
            + str(lat)
            + "&lon="
            + str(lng)
            + "&radius=700&bu=null&collection=aem_commercial_dealers&banner=GCR"
        )

        loclist = session.get(url, headers=headers).json()

        for loc in loclist:

            pcode = loc["postalCode"]
            street = loc["streetAddress"]
            phone = loc["businessPhone"]
            if "-" not in phone:
                phone = phone[0:3] + "-" + phone[3:6] + "-" + phone[6:]
            store = loc["locationNo"]
            title = loc["tradeName"]
            ccode = loc["country"]
            city = loc["city"]
            state = loc["state"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            hours = ""
            for day in daylist:
                day = day + "day"
                try:
                    closestr = loc[day + "Close"]
                except:
                    hours = hours + day + " " + " Close "
                    continue
                close = int(closestr.split(":", 1)[0])
                if close > 12:
                    close = close - 12
                hours = (
                    hours
                    + day
                    + " "
                    + loc[day + "Open"]
                    + " AM - "
                    + str(close)
                    + ":"
                    + closestr.split(":", 1)[1]
                    + " PM "
                )
            link = "https://www.gcrtires.com/stores" + loc["externalPath"]
            if link in storelist:
                continue
            storelist.append(link)

            yield SgRecord(
                locator_domain="https://www.gcrtires.com/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=str(store),
                phone=phone.strip(),
                location_type="<MISSING>",
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
