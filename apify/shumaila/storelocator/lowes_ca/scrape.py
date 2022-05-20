from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgrequests import SgRequests
from sgzip.static import static_coordinate_list
from sgzip.dynamic import SearchableCountries

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
}


def fetch_data():

    mylist = static_coordinate_list(70, SearchableCountries.CANADA)

    for latnow, lngnow in mylist:

        url = "https://www.lowes.ca/stores/fetch/gcpToken"
        mauth = session.get(url, headers=headers).json()["access_token"]
        url = (
            "https://api-prod.lowes.com/v2/storeinfoservices/stores?maxResults=10&responseGroup=large&countryCode=CA&query="
            + str(latnow)
            + ","
            + str(lngnow)
        )

        headers1 = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "authority": "api-prod.lowes.com",
            "method": "GET",
            "path": url.replace("https://api-prod.lowes.com", ""),
            "scheme": "https",
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br",
            "accept-language": "en-US,en;q=0.9",
            "auth-host": "undefined",
            "authorization": "Bearer " + mauth,
            "content-type": "application/json;charset=utf-8",
            "dtqlws": "true",
            "origin": "https://www.lowes.ca",
            "referer": "https://www.lowes.ca/",
            "sec-ch-ua": '"Chromium";v="94", "Google Chrome";v="94", ";Not A Brand";v="99"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"Windows"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "cross-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36",
            "x-api-version": "v4",
            "x-lowes-uuid": "1234",
        }

        loclist = session.get(url, headers=headers1).json()

        for loc in loclist:
            try:
                loc = loc["store"]
            except:
                continue
            pcode = loc["zip"]
            ccode = "CA"
            street = loc["address"]
            longt = loc["long"]
            lat = loc["lat"]
            phone = loc["phone"]
            title = loc["store_name"]
            store = loc["id"]
            state = loc["state"]
            city = loc["city"]
            hourlist = loc["storeHours"]
            link = "https://www.lowes.ca/stores/" + loc["bis_name"]

            hours = ""
            for hr in hourlist:
                hr = hr["day"]
                day = hr["day"]
                start = hr["open"].split(".")
                start = ":".join(start[0:2])
                endtime = (int)(hr["close"].split(".", 1)[0])
                if endtime > 12:
                    endtime = endtime - 12
                close = str(endtime) + ":00 PM "
                hours = hours + day + " " + start + " AM - " + close
            yield SgRecord(
                locator_domain="https://www.lowes.ca/",
                page_url=link,
                location_name=title,
                street_address=street.strip(),
                city=city.strip(),
                state=state.strip(),
                zip_postal=pcode.strip(),
                country_code=ccode,
                store_number=store,
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
