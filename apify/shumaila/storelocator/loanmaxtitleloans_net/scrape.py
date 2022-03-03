from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgzip.dynamic import SearchableCountries
from sgzip.static import static_zipcode_list

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36",
    "content-type": "application/json; charset=UTF-8",
}


def fetch_data():
    data = []
    url = "https://api.selectmgmt.com/api/apiMarketing/GetStores"
    zips = static_zipcode_list(radius=200, country_code=SearchableCountries.USA)

    for zip_code in zips:

        dataobj = (
            '{"lat":0,"lon":0,"zip":'
            + str(zip_code)
            + ',"distance":1000,"webSite":"www.loanmaxtitleloans.net","state":"","city":"","addr":""}'
        )
        try:
            loclist = session.post(url, data=dataobj, headers=headers).json()[
                "locations"
            ]
        except:
            continue
        for loc in loclist:

            store = loc["id"]
            title = loc["fullName"]
            street = loc["street"]
            state = loc["state"]
            city = loc["city"]
            pcode = loc["zip"]
            lat = loc["lat"]
            longt = loc["lon"]
            phone = loc["phone"]
            hourlist = loc["StoreHoursFormatted"]
            link = "https://www.loanmaxtitleloans.net/locations" + loc["urlParams"]
            hours = ""

            for hr in hourlist:
                day = hr["MinDay"] + "-" + hr["MaxDay"]
                timestr = hr["HourRange"]
                hours = hours + day + " " + timestr + " "
            if link in data:
                continue
            data.append(link)
            yield SgRecord(
                locator_domain="https://www.loanmaxtitleloans.net/",
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
