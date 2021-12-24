from sgrequests import SgRequests
import json
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

session = SgRequests()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}


def fetch_data():

    mylist = DynamicGeoSearch(country_codes=SearchableCountries.ALL)

    for lat, lng in mylist:

        headers = {
            "Connection": "keep-alive",
            "sec-ch-ua": '"Google Chrome";v="95", "Chromium";v="95", ";Not A Brand";v="99"',
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/json",
            "X-Requested-With": "XMLHttpRequest",
            "sec-ch-ua-mobile": "?0",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
            "sec-ch-ua-platform": '"Linux"',
            "Origin": "https://stores.crocs.com",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Dest": "empty",
            "Referer": "https://stores.crocs.com/index_new_int.html",
            "Accept-Language": "en-US,en;q=0.9",
        }

        data = {
            "request": {
                "appkey": "1BC4F6AA-9BB9-11E6-953B-FA25F3F215A2",
                "formdata": {
                    "geoip": False,
                    "dataview": "store_default",
                    "order": "tblstoretype DESC,_distance",
                    "limit": 100000,
                    "geolocs": {
                        "geoloc": [{"latitude": f"{lat}", "longitude": f"{lng}"}]
                    },
                    "searchradius": "100",
                    "radiusuom": "mile",
                    "where": {
                        "tblstorestatus": {"in": "Open,OPEN,open"},
                        "or": {
                            "crocsretail": {"eq": "1"},
                            "crocsoutlet": {"eq": "1"},
                            "otherretailer": {"eq": "1"},
                        },
                    },
                    "false": "0",
                },
            }
        }
        try:
            loclist = session.post(
                "https://stores.crocs.com/rest/locatorsearch",
                headers=headers,
                data=json.dumps(data),
            ).json()["response"]["collection"]
        except:
            continue
        weeklist = ["mon", "tue", "wed", "thr", "fri", "sat", "sun"]
        for loc in loclist:
            title = loc["name"]
            store = loc["clientkey"]
            phone = loc["phone"]
            city = loc["city"]
            state = loc["state"]
            pcode = loc["postalcode"]
            lat = loc["latitude"]
            longt = loc["longitude"]
            try:
                street = loc["address1"] + " " + str(loc["address2"])

                street = street.replace("&#xa0;", " ").replace("&#x96;", " ").strip()
            except:
                continue
            street = street.replace("None", "")
            ccode = loc["country"]
            ltype = "Outlet"
            hours = "<MISSING>"

            if loc["crocsoutlet"] == 0:
                ltype = "Dealer"

                link = "<MISSING>"
            else:
                hours = ""
                try:
                    link = (
                        "https://locations.crocs.com/"
                        + state
                        + "-"
                        + city
                        + "-"
                        + str(store)
                    )
                except:
                    link = "<MISSING>"
                try:
                    for day in weeklist:
                        hours = hours + day + " " + loc[day] + " "
                except:
                    hours = "<MISSING>"
            yield SgRecord(
                locator_domain="https://www.crocs.com/",
                page_url=link,
                location_name=title,
                street_address=street,
                city=city,
                state=state,
                zip_postal=pcode,
                country_code=ccode,
                store_number=str(store),
                phone=phone,
                location_type=ltype,
                latitude=str(lat),
                longitude=str(longt),
                hours_of_operation=hours,
            )


def scrape():

    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:
        results = fetch_data()
        for rec in results:
            writer.write_row(rec)


scrape()
