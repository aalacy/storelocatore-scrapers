from sglogging import sglog

from sgzip.dynamic import DynamicGeoSearch, SearchableCountries
from sgzip.static import static_zipcode_list

from sgscrape import simple_scraper_pipeline as sp
from sgscrape import simple_utils as utils
from sgscrape import sgpostal as parser

from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4


def get_apiKey():
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    url = "https://locator.networkhq.org/js/locator.js"
    session = SgRequests()
    nastyJS = session.get(url, headers=headers).text

    key = nastyJS.split("apikey=", 1)[1].split("'", 1)[0]
    return key


def para(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    try:
        resp = session.get(
            "https://www.partsplus.com/stores.wws?zipoverride=" + str(url),
            headers=headers,
        )
        link = str(resp.url)
    except Exception:
        link = "Missing"

    return {"url": str(link + "stores.wws"), "zip": url}


def paraThis(url):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")

    k = {}

    k["data"] = {}
    k["parsed"] = {}
    k["data"]["websiteUrl"] = url
    stuff = soup.find("div", {"class": lambda x: x and "locator-address-time" in x})
    stuff = stuff.find("div", {"class": "col-sm-6"})

    try:
        k["data"]["name"] = stuff.find("h2").text.strip()
    except Exception:
        k["data"]["name"] = "<MISSING>"
    k["data"]["latitude"] = "<MISSING>"
    k["data"]["longitude"] = "<MISSING>"
    addressData = stuff.find("ul", {"class": "locator-address"}).find_all("li")
    rawa = []
    phone = []
    for i in addressData:
        if "Phone" not in i.text:
            rawa.append(" ".join(list(i.stripped_strings)))
        else:
            for j in i.text:
                if j.isdigit():
                    phone.append(j)
    rawa = " ".join(rawa)
    phone = "".join(phone)
    parsedAddress = parser.parse_address_usa(rawa)
    k["parsed"]["address"] = parsedAddress.street_address_1
    if parsedAddress.street_address_2:
        k["parsed"]["address"] = (
            k["parsed"]["address"] + ", " + parsedAddress.street_address_2
        )

    k["parsed"]["city"] = parsedAddress.city if parsedAddress.city else "<MISSING>"
    k["parsed"]["state"] = parsedAddress.state if parsedAddress.state else "<MISSING>"
    k["parsed"]["zip"] = (
        parsedAddress.postcode if parsedAddress.postcode else "<MISSING>"
    )
    k["parsed"]["raw"] = rawa
    k["data"]["country"] = (
        parsedAddress.country if parsedAddress.country else "<MISSING>"
    )
    k["data"]["phone"] = phone
    k["data"]["companyLocationId"] = "<MISSING>"

    hoursData = list(stuff.find("ul", {"class": "locator-timing"}).stripped_strings)

    k["data"]["hours"] = "Ingonyama nengw enamabala" + ": ".join(hoursData)
    k["data"]["hours"] = k["data"]["hours"].replace("pm:", "pm;")
    k["data"]["serviceDealerType"] = "<MISSING>"

    if not k["parsed"]["address"]:
        k["parsed"]["address"] = "<MISSING>"
    if not k["parsed"]["city"]:
        k["parsed"]["city"] = "<MISSING>"
    if not k["parsed"]["state"]:
        k["parsed"]["state"] = "<MISSING>"
    if not k["parsed"]["zip"]:
        k["parsed"]["zip"] = "<MISSING>"

    return k


def start_somewhere(url, done):
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }
    session = SgRequests()
    soup = b4(session.get(url, headers=headers).text, "lxml")
    done.append(url)

    try:
        url = url.split("stores.wws")[0]
    except Exception:
        url = url

    try:
        url = url.split("pickupstoredisplay.wws?")[0]
    except Exception:
        url = url

    tags = soup.find_all(
        "a", {"href": lambda x: x and "pickupstoredisplay.wws?storenum=" in x}
    )
    if len(tags) == 0 and str(url + "pickupstoredisplay.wws?storenum=1") not in done:
        start_somewhere(str(url + "pickupstoredisplay.wws?storenum=1"), done)
    for i in tags:
        link = str(
            url
            + "pickupstoredisplay.wws?"
            + str(i["href"].split("pickupstoredisplay.wws?", 1)[1])
        )
        if link not in done:
            done = start_somewhere(link, done)
    return done


def fetch_data():
    logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
    url = "https://em.networkhq.org/CompanyLocations/GetServiceDealerLocationsInRange?lat="
    ext = "&distance=2000&unitOfMeasure=miles&apikey="
    headers = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
    }

    logzilla.info(f"Figuring out API key..")  # noqa
    apiKey = get_apiKey()
    # Highly unlikely that api key changes mid-run, leaving it here is probably a-ok.
    logzilla.info(f"Found this: {apiKey}")  # noqa

    search = DynamicGeoSearch(
        country_codes=[SearchableCountries.CANADA, SearchableCountries.USA],
        max_radius_miles=2000,
    )
    identities = set()
    otherIdent = set()
    maxZ = search.items_remaining()
    total = 0
    for lat, lng in search:
        if search.items_remaining() > maxZ:
            maxZ = search.items_remaining()
        found = 0
        session = SgRequests()
        son = session.get(
            url + str(lat) + "&lon=" + str(lng) + ext + str(apiKey), headers=headers
        ).json()
        for i in son:
            search.found_location_at(i["latitude"], i["longitude"])
            if i["companyLocationId"] not in identities:
                k = {}
                parsedAddress = parser.parse_address_usa(
                    str(i["address1"] if i["address1"] else "")
                    + ", "
                    + str(i["address2"] if i["address2"] else "")
                )
                k["address"] = (
                    parsedAddress.street_address_1
                    if parsedAddress.street_address_1
                    else ""
                )
                if parsedAddress.street_address_2:
                    k["address"] = k["address"] + ", " + parsedAddress.street_address_2

                k["city"] = parsedAddress.city if parsedAddress.city else "<MISSING>"
                k["state"] = parsedAddress.state if parsedAddress.state else "<MISSING>"
                k["zip"] = (
                    parsedAddress.postcode if parsedAddress.postcode else "<MISSING>"
                )
                k["raw"] = (
                    str(i["address1"] if i["address1"] else "")
                    + ", "
                    + str(i["address2"] if i["address2"] else "")
                )
                identities.add(i["companyLocationId"])
                found += 1
                if (
                    str(k["address"] + k["city"] + k["state"] + k["zip"])
                    not in otherIdent
                ):
                    otherIdent.add(
                        str(k["address"] + k["city"] + k["state"] + k["zip"])
                    )
                yield {"data": i, "parsed": k}

        progress = str(round(100 - (search.items_remaining() / maxZ * 100), 2)) + "%"
        total += found
        logzilla.info(
            f"{lat}, {lng} | found: {found} | total: {total} | progress: {progress}"
        )

    lize = utils.parallelize(
        search_space=static_zipcode_list(
            radius=100, country_code=SearchableCountries.USA
        ),
        fetch_results_for_rec=para,
        max_threads=10,
        print_stats_interval=50,
    )
    toCrawl = set()
    for i in lize:
        if i["url"] not in toCrawl and i["url"] != "Missingstores.wws":
            toCrawl.add(i["url"])

    toCrawl = list(toCrawl)

    for i in toCrawl:
        pages = start_somewhere(i, [])
        topop = []
        for j, val in enumerate(pages):
            if "stores.wws" in val:
                topop.append(j)
        for j in reversed(topop):
            pages.pop(j)
        lize = utils.parallelize(
            search_space=pages,
            fetch_results_for_rec=paraThis,
            max_threads=10,
            print_stats_interval=10,
        )
        for j in lize:
            try:
                recordIdent = str(
                    j["parsed"]["address"]
                    + j["parsed"]["city"]
                    + j["parsed"]["state"]
                    + j["parsed"]["zip"]
                )
            except Exception:
                logzilla.info(f"had troubles with this record : {j}")
                raise Exception

            if recordIdent not in otherIdent:
                otherIdent.add(recordIdent)
                yield j

    logzilla.info(f"Finished grabbing data!!")  # noqa


def human_hours(x):
    if "Ingonyama nengw enamabala" in x:
        return x.replace("Ingonyama nengw enamabala", "")
    h = []
    if len(x) > 1:
        for i in x:
            if i["isClosed"] == "False":
                h.append(
                    str(i["dayOfWeek"] + ": " + i["openTime"] + "-" + i["closeTime"])
                )
            else:
                h.append(str(i["dayOfWeek"] + ": Closed"))
        return "; ".join(h)
    else:
        return "<MISSING>"


def scrape():
    url = "https://www.partsplus.com/"
    field_defs = sp.SimpleScraperPipeline.field_definitions(
        locator_domain=sp.ConstantField(url),
        page_url=sp.MappingField(
            mapping=["data", "websiteUrl"],
            value_transform=lambda x: x.replace("None", ""),
            is_required=False,
        ),
        location_name=sp.MappingField(
            mapping=["data", "name"],
        ),
        latitude=sp.MappingField(mapping=["data", "latitude"], is_required=False),
        longitude=sp.MappingField(mapping=["data", "longitude"], is_required=False),
        street_address=sp.MappingField(
            mapping=["parsed", "address"],
        ),
        city=sp.MappingField(
            mapping=["parsed", "city"],
        ),
        state=sp.MappingField(
            mapping=["parsed", "state"],
            is_required=False,
        ),
        zipcode=sp.MappingField(
            mapping=["parsed", "zip"],
        ),
        country_code=sp.MappingField(mapping=["data", "country"], is_required=False),
        phone=sp.MappingField(mapping=["data", "phone"], is_required=False),
        store_number=sp.MappingField(
            mapping=["data", "companyLocationId"], is_required=False
        ),
        hours_of_operation=sp.MappingField(
            mapping=["data", "hours"],
            raw_value_transform=human_hours,
            is_required=False,
        ),
        location_type=sp.MappingField(
            mapping=["data", "serviceDealerType"], is_required=False
        ),
        raw_address=sp.MappingField(mapping=["parsed", "raw"], is_required=False),
    )

    pipeline = sp.SimpleScraperPipeline(
        scraper_name="pipeline",
        data_fetcher=fetch_data,
        field_definitions=field_defs,
        log_stats_interval=50,
    )

    pipeline.run()


if __name__ == "__main__":
    scrape()
