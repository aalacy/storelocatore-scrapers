from sglogging import sglog
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
from sgzip.utils import country_names_by_code
from fuzzywuzzy import process
from sgzip.dynamic import DynamicGeoSearch, Grain_8

logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")


def fix_german(text):
    return (
        text.replace("Ä", "AE")
        .replace("ä", "ae")
        .replace("Ö", "OE")
        .replace("ö", "oe")
        .replace("Ü", "UE")
        .replace("ü", "ue")
        .replace("ß", "ss")
    )


def human_hours(rawHrs):
    days = ["", "Mo.", "Di.", "Mi.", "Do.", "Fr.", "Sa.", "So"]
    human_hrs = []
    for day in rawHrs:
        dayString = days[day["dayOfWeek"]] + ": "
        intervals = list(day.values())
        intervals.pop(0)
        intervalsLen = len(intervals)
        interval = 0
        while interval < intervalsLen:
            if type(intervals[interval]) == bool:
                dayString = dayString + "24/7"
                break
            if interval % 2 == 0:
                dayString = dayString + intervals[interval]
            else:
                dayString = dayString + "-" + intervals[interval]
            interval += 1
        human_hrs.append(dayString)
    return "; ".join(human_hrs)


def transform_germany(raw):
    good = {}
    good["locator_domain"] = raw["locator_domain"]
    good["location_name"] = raw["name"]
    good["latitude"] = raw["lat"]
    good["longitude"] = raw["lng"]
    good["street_address"] = raw["streetAndNumber"]
    good["city"] = raw["city"]
    good[
        "page_url"
    ] = "https://www.mcdonalds.com/de/de-de/restaurant-suche.html/l/{}/{}/{}".format(
        fix_german(good["city"]),
        fix_german(good["street_address"]).replace(" ", "-"),
        raw["identifier"],
    )
    good["state"] = raw["province"]
    good["zipcode"] = raw["zip"]
    good["country_code"] = raw["country"]
    good["phone"] = raw["phone"]
    good["store_number"] = raw["id"]
    good["hours_of_operation"] = human_hours(raw["openingHours"])
    good["location_type"] = ""
    good["raw_address"] = ""

    return good


def fetch_data(session, apiKey, country):
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    url = "https://uberall.com/api/storefinders/{}/locations/all?v=20171219&language=de&full=true&identifier=true".format(
        apiKey
    )
    data = session.get(url, headers=headers).json()
    for store in data["response"]["locations"]:
        store["locator_domain"] = country["page"]
        yield transform_germany(store)


def getAPIKey(session, country, url):
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = b4(session.get(url, headers=headers).text, "lxml")
    apiKey = soup.find(
        "div",
        {
            "id": "store-finder-widget",
            "data-key": True,
            "data-showheader": True,
            "data-language": True,
        },
    )
    if apiKey:
        apiKey = apiKey["data-key"]
    return apiKey


def getLocsPage(session, country):
    if "kraine" in country["text"]:
        return "/ua/uk-ua/finn-oss.html"
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = session.get(country["page"], headers=headers).text
    soup = b4(soup, "lxml")
    locsPage = soup.find(
        "a",
        {
            "href": True,
            "class": True,
            "target": True,
            "data-at": lambda x: x and "avintol" in x,
            "data-track": lambda x: x and "topLinks" in x,
        },
    )
    return locsPage["href"] if locsPage else locsPage


def strip_domain(country):
    return "/".join(country.split("/")[0:3])


def determine_country(country):
    Searchable = country_names_by_code()
    resultName = process.extract(country["text"], list(Searchable.values()), limit=1)
    resultCode = process.extract(
        country["page"].split("//")[1].split("/")[1], list(Searchable.keys()), limit=1
    )
    logzilla.info(
        f"Matched {country['text']} - {country['page']} to {resultName[0]} or {resultCode[0]}"
    )
    if resultName[-1][-1] > resultCode[-1][-1]:
        for i in Searchable.items():
            if i[1] == resultName[-1][0]:
                return i[0]
    else:
        return resultCode[-1][0]


def fix_comma(x):
    h = []
    try:
        for i in x.split(","):
            if len(i.strip()) >= 1:
                h.append(i)
        return ", ".join(h)
    except Exception:
        return x


def transform_item_map(raw, country):
    good = {}
    good["locator_domain"] = country["page"]
    good["location_name"] = raw["properties"]["name"]
    good["latitude"] = raw["geometry"]["coordinates"][-1]
    good["longitude"] = raw["geometry"]["coordinates"][0]
    good["street_address"] = ""
    try:
        raw["properties"]["addressLine1"] = raw["properties"]["addressLine1"]
        good["street_address"] = raw["properties"]["addressLine1"]
    except Exception:
        pass
    try:
        raw["properties"]["addressLine2"] = raw["properties"]["addressLine2"]
        good["street_address"] = (
            good["street_address"] + ", " + raw["properties"]["addressLine2"]
        )
    except Exception:
        pass
    good["street_address"] = fix_comma(good["street_address"])
    try:
        good["city"] = raw["properties"]["addressLine3"]
    except Exception:
        good["city"] = ""
    rightID = None
    for i in raw["properties"]["identifiers"]["storeIdentifier"]:
        if i["identifierType"] == "LocalRefNum":
            rightID = i["identifierValue"]
    good["page_url"] = "{}/location///{}.html".format(
        country["page"].replace(".html", ""), str(rightID)
    )
    try:
        good["state"] = raw["properties"]["subDivision"]
    except Exception:
        good["state"] = ""
    good["zipcode"] = raw["properties"]["postcode"]
    good["country_code"] = raw["properties"]["addressLine4"]
    try:
        raw["properties"]["telephone"] = raw["properties"]["telephone"]
        good["phone"] = raw["properties"]["telephone"]
    except Exception:
        pass
    good["store_number"] = raw["properties"]["id"]
    good["hours_of_operation"] = str(raw["properties"]["restauranthours"]).replace(
        '"', " "
    )
    good["hours_of_operation"] = (
        good["hours_of_operation"]
        .replace("{", "")
        .replace("}", "")
        .replace("hours", "")
        .replace("'", "")
    )
    good["location_type"] = (
        str(raw["properties"]["filterType"])
        .replace("'", "")
        .replace("[", "")
        .replace("]", "")
    )
    good["raw_address"] = ""
    return good


def strip_locale(country):
    return country.split("//")[1].split("/")[1:3]


def pull_map_poi(coord, url, session, locale, lang, country):
    lat, lng = coord
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    data = session.get(
        url.format(lat=lat, lng=lng, locale=locale, lang=lang), headers=headers
    ).json()
    for raw in data["features"]:
        good = transform_item_map(raw, country)
        yield good


def pull_from_map(session, country):
    url = "https://www.mcdonalds.com/googleappsv2/geolocation?latitude={lat}&longitude={lng}&radius=300&maxResults=75&country={locale}&language={lang}&showClosed=&hours24Text=Open%2024%20hr"
    locale, lang = strip_locale(country["page"])
    lang = lang.replace(".html", "")
    SearchableCountry = determine_country(country)
    search = None
    try:
        search = DynamicGeoSearch(
            country_codes=[SearchableCountry],
            expected_search_radius_miles=None,
            max_search_results=None,
            granularity=Grain_8(),
        )
    except Exception as e:
        logzilla.warning(
            f"Issue with sgzip and country code: {SearchableCountry}\n{e}\n"
        )
    lang2 = lang.split("-")[1]
    lang2 = "en-" + lang
    if search:
        with SgRequests(proxy_country=locale) as session2:
            for coord in search:
                try:
                    for rec in pull_map_poi(
                        coord, url, session2, locale, lang, country
                    ):
                        search.found_location_at(rec["latitude"], rec["longitude"])
                        yield rec
                except Exception:
                    pass
                try:
                    for rec in pull_map_poi(
                        coord, url, session2, locale, lang2, country
                    ):
                        search.found_location_at(rec["latitude"], rec["longitude"])
                        yield rec
                except Exception:
                    pass


def test_for_map(locationsPage, country, session, domain):
    if "kraine" in country["text"]:
        return True
    headers = {}
    headers[
        "user-agent"
    ] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    soup = session.get(domain + locationsPage, headers=headers).text
    if "map-list-view" in soup:
        return True
    else:
        return None


def fetch_germany_ISH(country):
    domain = strip_domain(country["page"])
    with SgRequests() as session:
        logzilla.info(f"Attempting to pull {country['text']}")
        locationsPage = getLocsPage(session, country)
        if locationsPage:
            logzilla.info(f"Found locations page {locationsPage}\nLooking for API key")
            apiKey = getAPIKey(session, country, str(domain + locationsPage))
        if locationsPage and apiKey:
            logzilla.info(f"Onto something with {country['text']}\nAPI Key: {apiKey}")
            for rec in fetch_data(session, apiKey, country):
                yield rec
        elif locationsPage:
            isMap = test_for_map(locationsPage, country, session, domain)
            if isMap:
                logzilla.info(f"Map test passed!")  # noqa
                for rec in pull_from_map(session, country):
                    yield rec


if __name__ == "__main__":
    pass
