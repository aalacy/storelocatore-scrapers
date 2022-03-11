from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord import SgRecord
from sgscrape.sgrecord_id import RecommendedRecordIds
from sgscrape.sgrecord_deduper import SgRecordDeduper

from sgrequests import SgRequests

log = SgLogSetup().get_logger("newyorkfries.com")


def fetch_data(sgw: SgWriter):

    base_link = "https://www.newyorkfries.com/locations-new"

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    req = session.get(base_link, headers=headers)
    base = BeautifulSoup(req.text, "lxml")

    locator_domain = "newyorkfries.com"

    items = base.find_all(role="gridcell")

    headers = {
        "authority": "www.newyorkfries.com",
        "method": "POST",
        "accept": "*/*",
        "authorization": "wixcode-pub.736b864132b36e4594f1a1dded955c1509b3e025.eyJpbnN0YW5jZUlkIjoiYTA2NTRkYTktZDE1Yi00M2E2LTg5MjUtMjgwNjE5ZjE4N2VlIiwiaHRtbFNpdGVJZCI6IjMxOGU2YzViLTE5ZWItNGMyNi1iNWVhLWRkYTM4M2E3ZTRmYiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTY0NjgxNjQ4NzI0MywiYWlkIjoiYjUzZDZjZGYtYWIzMC00MDNiLTljMGYtNGRkMzk1NDk3ZjI4IiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImI4YTg3MmExLTMwMDMtNDQ5Yy05MWM0LWU1YzBlZDk2MTFlZCIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsU2hvd1dpeFdoaWxlTG9hZGluZyxIYXNEb21haW4iLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiYmRmOGI2ODAtYWY4ZC00ODI5LWIxY2YtNDkwY2UzZDJhMDc0IiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ==",
        "accept-encoding": "gzip, deflate, br",
        "x-wix-grid-app-id": "29982d3f-dbc4-46be-8c5b-4e18b6368e82",
        "x-xsrf-token": "1646812932|lfEa5YScQUnS",
        "sec-fetch-user": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36",
    }

    for item in items:

        raw_data = list(item.stripped_strings)

        location_name = raw_data[0].strip()
        location_type = raw_data[1].strip()
        city = raw_data[2].strip()
        state = raw_data[3].strip()

        link = item.a["href"]
        log.info(link)
        api_link = "https://www.newyorkfries.com/_api/dynamic-pages-router/v1/pages?gridAppId=29982d3f-dbc4-46be-8c5b-4e18b6368e82&viewMode=site&instance=wixcode-pub.cd98203189b60a26cd55c6600992b367001186ef.eyJpbnN0YW5jZUlkIjoiYTA2NTRkYTktZDE1Yi00M2E2LTg5MjUtMjgwNjE5ZjE4N2VlIiwiaHRtbFNpdGVJZCI6IjMxOGU2YzViLTE5ZWItNGMyNi1iNWVhLWRkYTM4M2E3ZTRmYiIsInVpZCI6bnVsbCwicGVybWlzc2lvbnMiOm51bGwsImlzVGVtcGxhdGUiOmZhbHNlLCJzaWduRGF0ZSI6MTY0NjgxNDU0MzIxNiwiYWlkIjoiYjUzZDZjZGYtYWIzMC00MDNiLTljMGYtNGRkMzk1NDk3ZjI4IiwiYXBwRGVmSWQiOiJDbG91ZFNpdGVFeHRlbnNpb24iLCJpc0FkbWluIjpmYWxzZSwibWV0YVNpdGVJZCI6ImI4YTg3MmExLTMwMDMtNDQ5Yy05MWM0LWU1YzBlZDk2MTFlZCIsImNhY2hlIjpudWxsLCJleHBpcmF0aW9uRGF0ZSI6bnVsbCwicHJlbWl1bUFzc2V0cyI6IkFkc0ZyZWUsU2hvd1dpeFdoaWxlTG9hZGluZyxIYXNEb21haW4iLCJ0ZW5hbnQiOm51bGwsInNpdGVPd25lcklkIjoiYmRmOGI2ODAtYWY4ZC00ODI5LWIxY2YtNDkwY2UzZDJhMDc0IiwiaW5zdGFuY2VUeXBlIjoicHViIiwic2l0ZU1lbWJlcklkIjpudWxsfQ%3D%3D"
        js = {
            "routerPrefix": "/locations",
            "routerSuffix": link.split("locations")[-1],
            "fullUrl": link,
            "config": {
                "patterns": {
                    "/{locationName}": {
                        "pageRole": "6d4cd4fd-fd24-4c7c-be54-bdb564ad71a1",
                        "title": "{locationName}",
                        "config": {
                            "collection": "LocationsCanada",
                            "pageSize": 1,
                            "lowercase": "true",
                        },
                        "seoMetaTags": {"og:image": "{acceptsFrySociety}"},
                    }
                }
            },
            "pageRoles": {
                "6d4cd4fd-fd24-4c7c-be54-bdb564ad71a1": {
                    "id": "v79cd",
                    "title": "Locations (Location Name)",
                }
            },
            "requestInfo": {"env": "browser", "formFactor": "desktop"},
        }
        try:
            stores = session.post(api_link, headers=headers, json=js).json()["result"][
                "data"
            ]["items"]
        except:
            session = SgRequests()
            stores = session.post(api_link, headers=headers, json=js).json()["result"][
                "data"
            ]["items"]

        for store in stores:
            try:
                street_address = (
                    store["streetAddress"].split("(")[0].split(", Montr")[0].strip()
                )
            except:
                continue
            city = store["city"]
            state = store["province"]
            try:
                zip_code = store["addressFull"]["postalCode"]
                latitude = store["addressFull"]["location"]["latitude"]
                longitude = store["addressFull"]["location"]["longitude"]
                country_code = store["addressFull"]["country"]
                store_number = store["storeId"]
            except:
                zip_code = ""
                latitude = ""
                longitude = ""
                country_code = "CA"
                store_number = ""
            if "V5H 4M5" in street_address:
                zip_code = "V5H 4M5"
                street_address = street_address.split(",")[0].strip()
            if "H4B 1V8" in store["streetAddress"]:
                zip_code = "H4B 1V8"
            phone = "<MISSING>"
            hours_of_operation = "<MISSING>"

            sgw.write_row(
                SgRecord(
                    locator_domain=locator_domain,
                    page_url=link,
                    location_name=location_name,
                    street_address=street_address,
                    city=city,
                    state=state,
                    zip_postal=zip_code,
                    country_code=country_code,
                    store_number=store_number,
                    phone=phone,
                    location_type=location_type,
                    latitude=latitude,
                    longitude=longitude,
                    hours_of_operation=hours_of_operation,
                )
            )


with SgWriter(SgRecordDeduper(RecommendedRecordIds.PageUrlId)) as writer:
    fetch_data(writer)
