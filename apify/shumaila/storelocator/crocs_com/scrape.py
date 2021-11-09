from sgscrape.sgrecord import SgRecord
from sgrequests import SgRequests
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.pause_resume import CrawlStateSingleton
from concurrent import futures
from sglogging import sglog
from sgzip.dynamic import SearchableCountries, DynamicGeoSearch

session = SgRequests()
locator_domain = "crocs_com"
log = sglog.SgLogSetup().get_logger(logger_name=locator_domain)


def get_data(coord, sgw: SgWriter):
    lat, lng = coord
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
                "geolocs": {"geoloc": [{"latitude": f"{lat}", "longitude": f"{lng}"}]},
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
        return
    weeklist = ["mon", "tue", "wed", "thr", "fri", "sat", "sun"]
    for loc in loclist:
        title = loc["name"]
        store = loc["clientkey"]
        phone = loc["phone"]
        city = loc["city"]
        state = loc["state"]
        street = loc["address1"] + " " + str(js["address2"])
        street = street.replace("None")
        ccode = loc["country"]
        ltype = "Outlet"
        hours = "<MISSING>"
        if loc["crocsoutlet"] == 0:
            ltype = "Dealer"

            link = "<MISSING>"
        else:
            hours = ""
            link = (
                "https://locations.crocs.com/" + state + "-" + city + "-" + str(store)
            )
            for day in weeklist:
                hours = hours + day + " " + loc[day] + " "
        yield SgRecord(
            locator_domain="https://www.crocs.com/",
            page_url=link,
            location_name=title,
            street_address=street.strip(),
            city=city.strip(),
            state=state.strip(),
            zip_postal=pcode.strip(),
            country_code=ccode,
            store_number=str(store),
            phone=phone,
            location_type=ltype,
            latitude=str(lat),
            longitude=str(longt),
            hours_of_operation=hours,
        )


def fetch_data(sgw: SgWriter):

    coords = DynamicGeoSearch(country_codes=SearchableCountries.ALL)

    with futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_url = {
            executor.submit(get_data, coord, sgw): coord for coord in coords
        }
        for future in futures.as_completed(future_to_url):
            future.result()


if __name__ == "__main__":

    session = SgRequests()
    with SgWriter(
        deduper=SgRecordDeduper(
            RecommendedRecordIds.StoreNumberId, duplicate_streak_failure_factor=-1
        )
    ) as writer:

        fetch_data(writer)
