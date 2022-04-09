from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgrequests.sgrequests import SgRequests
from sgzip.dynamic import SearchableCountries, Grain_1_KM
from sgzip.dynamic import DynamicGeoSearch
from sglogging import sglog

# This is a code change

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def strip_para(x):
    copy = []
    inside = False
    for i in x:
        if i == "<" or inside:
            inside = True
            continue
        elif i == ">":
            inside = False
            continue
        else:
            copy.append(i)
    return "".join(copy)


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def replac(x):
    x = str(x)
    x = x.replace("'", "").replace("(", "").replace(")", "").replace(",", "")
    if len(x) < 1:
        return "<MISSING>"
    return x


class ExampleSearchIteration:
    def do(search, coord, http1):
        lat, lng = coord
        numbers = "21%2C20"
        nCA = "93%2C91%2C90"
        nUS = "8%2C10%2C28%2C29%2C50"
        nAU = "20"
        if search.current_country() == "ca":
            numbers = nCA
        elif search.current_country() == "us":
            numbers = nUS
        elif search.current_country() == "au":
            numbers = nAU
        elif search.current_country() == "nf":
            numbers = nAU
        elif search.current_country() == "cx":
            numbers = nAU

        url = str(
            f"https://marketingsl.tjx.com/storelocator/GetSearchResults?geolat={lat}&geolong={lng}&chain={numbers}&maxstores=25&radius=100"
        )
        headers = {}
        headers["accept"] = "*/*"
        headers["accept-encoding"] = "gzip, deflate, br"
        headers["accept-language"] = "en-US,en;q=0.9,ro;q=0.8,es;q=0.7"
        headers["cache-control"] = "no-cache"
        headers["origin"] = "https://www.tjx.com"
        headers["pragma"] = "no-cache"
        headers["referer"] = "https://www.tjx.com/"
        headers[
            "sec-ch-ua"
        ] = '" Not A;Brand";v="99", "Chromium";v="98", "Google Chrome";v="98"'
        headers["sec-ch-ua-mobile"] = "?0"
        headers["sec-ch-ua-platform"] = '"Windows"'
        headers["sec-fetch-dest"] = "empty"
        headers["sec-fetch-mode"] = "cors"
        headers["sec-fetch-site"] = "same-site"
        headers[
            "user-agent"
        ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36"
        locations = None
        try:
            locations = SgRequests.raise_on_err(http1.get(url, headers=headers)).json()
        except Exception as e:
            logzilla.error(f"{e}")
        MISSING = "<MISSING>"
        if locations:
            if locations["Status"] == 0:
                for rec in locations["Stores"]:
                    location_name = str(
                        str(rec["Name"]).strip(),
                    )
                    street_address = str(
                        str(rec["Address"]).strip()
                        + ", "
                        + str(rec["Address2"]).strip(),
                    )
                    city = str(
                        str(rec["City"]).strip(),
                    )
                    state = str(
                        str(rec["State"]).strip(),
                    )
                    zip_postal = str(
                        str(rec["Zip"]).strip(),
                    )
                    country_code = str(
                        str(rec["Country"]).strip(),
                    )
                    store_number = str(
                        str(rec["StoreID"]).strip(),
                    )
                    phone = str(
                        str(rec["Phone"]).strip(),
                    )
                    location_type = str(
                        str(rec["Chain"]).strip(),
                    )
                    latitude = str(
                        rec["Latitude"],
                    )
                    longitude = str(
                        rec["Longitude"],
                    )
                    hours_of_operation = str(
                        strip_para(str(rec["Hours"])).strip(),
                    )
                    if latitude:
                        if longitude:
                            search.found_location_at(
                                replac(str(latitude)), replac(str(longitude))
                            )
                    yield SgRecord(
                        page_url=MISSING,
                        location_name=replac(location_name)
                        if location_name
                        else MISSING,
                        street_address=replac(fix_comma(street_address))
                        if street_address
                        else MISSING,
                        city=replac(city) if city else MISSING,
                        state=replac(state) if state else MISSING,
                        zip_postal=replac(zip_postal) if zip_postal else MISSING,
                        country_code=replac(country_code) if country_code else MISSING,
                        store_number=replac(store_number) if store_number else MISSING,
                        phone=replac(phone) if phone else MISSING,
                        location_type=replac(location_type)
                        if location_type
                        else MISSING,
                        latitude=replac(latitude) if latitude else MISSING,
                        longitude=replac(longitude) if longitude else MISSING,
                        locator_domain=MISSING,
                        hours_of_operation=replac(hours_of_operation)
                        if hours_of_operation
                        else MISSING,
                        raw_address=MISSING,
                    )


def dattafetch(search, http1):
    for coord in search:
        for item in ExampleSearchIteration.do(search, coord, http1):
            yield item


if __name__ == "__main__":
    tocrawl = []
    tocrawl.append(SearchableCountries.CANADA)
    tocrawl.append(SearchableCountries.USA)
    tocrawl.append(SearchableCountries.NORFOLK_ISLAND)
    tocrawl.append(SearchableCountries.CHRISTMAS_ISLAND)
    tocrawl.append(SearchableCountries.AUSTRALIA)
    tocrawl = tocrawl + SearchableCountries.ByGeography["CONTINENTAL_EUROPE"]
    tocrawl = tocrawl + SearchableCountries.SovereigntyGroups["UK"]
    search = DynamicGeoSearch(
        country_codes=tocrawl,
        granularity=Grain_1_KM(),
        expected_search_radius_miles=1.242742,
    )
    with SgWriter(
        deduper=SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                    SgRecord.Headers.PHONE,
                    SgRecord.Headers.STREET_ADDRESS,
                },
                fail_on_empty_id=True,
            ),
            duplicate_streak_failure_factor=-1,
        )
    ) as writer:
        with SgRequests() as http1:
            for rec in dattafetch(search, http1):
                writer.write_row(rec)
