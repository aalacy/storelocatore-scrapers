from sgscrape.sgrecord import SgRecord
from sgscrape.sgwriter import SgWriter
from sgscrape.sgrecord_id import SgRecordID
from sgscrape.sgrecord_deduper import SgRecordDeduper
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4
import json
import ssl

logger = SgLogSetup().get_logger(logger_name="Scraper")
ssl._create_default_https_context = ssl._create_unverified_context

headers_c = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

MISSING = SgRecord.MISSING
QUERY_LIMIT = 500
MAX_WORKERS = 10
API_ENDPOINT_URL = "https://www.hilton.com/graphql/customer?appName=dx_shop_search_app&operationName=hotelSummaryOptions_locationPage"


#  Those countries having more than 100 stores, it is listed here. This is used to paginate through sub-pages based on cities or provinces

highly_dense_state_or_country_list = [
    {"country_or_state_code": "CN", "c_or_s_name": "China", "count_current": "421"},
    {
        "country_or_state_code": "GB",
        "c_or_s_name": "United Kingdom",
        "count_current": "169",
    },
    {"country_or_state_code": "TX", "c_or_s_name": "Texas", "count_current": "544"},
    {"country_or_state_code": "FL", "c_or_s_name": "Florida", "count_current": "434"},
    {
        "country_or_state_code": "CA",
        "c_or_s_name": "California",
        "count_current": "395",
    },
    {"country_or_state_code": "GA", "c_or_s_name": "Georgia", "count_current": "240"},
    {
        "country_or_state_code": "NC",
        "c_or_s_name": "North Carolina",
        "count_current": "227",
    },
    {"country_or_state_code": "NY", "c_or_s_name": "New York", "count_current": "218"},
    {"country_or_state_code": "OH", "c_or_s_name": "Ohio", "count_current": "203"},
    {
        "country_or_state_code": "PA",
        "c_or_s_name": "Pennsylvania",
        "count_current": "201",
    },
    {"country_or_state_code": "VA", "c_or_s_name": "Virginia", "count_current": "197"},
    {"country_or_state_code": "TN", "c_or_s_name": "Tennessee", "count_current": "176"},
    {"country_or_state_code": "IL", "c_or_s_name": "Illinois", "count_current": "159"},
    {
        "country_or_state_code": "SC",
        "c_or_s_name": "South Carolina",
        "count_current": "145",
    },
    {"country_or_state_code": "AL", "c_or_s_name": "Alabama", "count_current": "127"},
    {"country_or_state_code": "IN", "c_or_s_name": "Indiana", "count_current": "125"},
    {"country_or_state_code": "MI", "c_or_s_name": "Michigan", "count_current": "123"},
    {"country_or_state_code": "AZ", "c_or_s_name": "Arizona", "count_current": "119"},
    {"country_or_state_code": "CO", "c_or_s_name": "Colorado", "count_current": "117"},
]


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(urlnum, country, url):
    path_per_country_or_state = url.split("/en/")[-1].rstrip("/")
    logger.info(f"{country} | {path_per_country_or_state}")
    payload1 = {
        "query": "query hotelSummaryOptions_locationPage($language: String!, $path: String!, $queryLimit: Int!, $currencyCode: String!, $distanceUnit: HotelDistanceUnit, $titleFormat: MarkdownFormatType!) {\n  locationPage(language: $language, path: $path) {\n    location {\n      interlinkTitle\n      interlinks {\n        uri\n        name\n      }\n      _id: uri\n      title(format: $titleFormat)\n      accessibilityTitle\n      meta {\n        pageTitle\n        description\n      }\n      name\n      brandCode\n      category\n      uri\n      globalBounds\n      breadcrumbs {\n        uri\n        name\n      }\n      about {\n        desc\n        headline\n        shortDesc\n      }\n      paths {\n        base\n      }\n    }\n    match {\n      address {\n        city\n        country\n        countryName\n        postalCode\n        state\n        stateName\n      }\n      geometry {\n        location {\n          latitude\n          longitude\n        }\n        bounds {\n          northeast {\n            latitude\n            longitude\n          }\n          southwest {\n            latitude\n            longitude\n          }\n        }\n      }\n      name\n      type\n    }\n    hotelSummaryOptions(distanceUnit: $distanceUnit, sortBy: distance) {\n      _hotels {\n        totalSize\n      }\n      bounds {\n        northeast {\n          latitude\n          longitude\n        }\n        southwest {\n          latitude\n          longitude\n        }\n      }\n      amenities {\n        id\n        name\n      }\n      amenityCategories {\n        name\n        id\n        amenityIds\n      }\n      brands {\n        code\n        name\n      }\n      hotels(first: $queryLimit) {\n        amenityIds\n        brandCode\n        ctyhocn\n        distance\n        distanceFmt\n        facilityOverview {\n          allowAdultsOnly\n          homeUrl\n        }\n        name\n        contactInfo {\n          phoneNumber\n        }\n        display {\n          open\n          openDate\n          preOpenMsg\n          resEnabled\n          resEnabledDate\n        }\n        disclaimers {\n          desc\n          type\n        }\n        address {\n          addressFmt\n          addressLine1\n          city\n          country\n          countryName\n          postalCode\n          state\n          stateName\n        }\n        localization {\n          currencyCode\n          coordinate {\n            latitude\n            longitude\n          }\n        }\n        masterImage(variant: searchPropertyImageThumbnail) {\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        leadRate {\n          lowest {\n            rateAmount(currencyCode: $currencyCode)\n            rateAmountFmt(decimal: 0, strategy: trunc)\n            ratePlan {\n              ratePlanName\n              ratePlanDesc\n            }\n          }\n        }\n      }\n    }\n  }\n}\n",
        "operationName": "hotelSummaryOptions_locationPage",
        "variables": {
            "path": path_per_country_or_state,
            "language": "en",
            "queryLimit": QUERY_LIMIT,
            "currencyCode": "USD",
            "titleFormat": "md",
        },
    }

    with SgRequests(timeout_config=600, verify_ssl=False) as http:
        logger.info(f"[{urlnum}] Pulling the data from: {url}")
        r = http.post(API_ENDPOINT_URL, data=json.dumps(payload1), headers=headers_c)
        if r.status_code == 200:
            if r.json() is not None:
                logger.info(f"HTTP Status Code: {r.status_code}")
                return r
        raise Exception(f"{urlnum} : {url} >> Temporary Error: {r.status_code}")


def fetch_records(idx, country_n_url, sgw: SgWriter):
    country_name = country_n_url["text"]
    country_link = country_n_url["link"]
    r = get_response(idx, country_name, country_link)
    data_json = r.json()
    try:
        if "hotelSummaryOptions" in data_json["data"]["locationPage"]:
            hotel_summary_options = data_json["data"]["locationPage"][
                "hotelSummaryOptions"
            ]
            if hotel_summary_options is not None:
                data_hotels = hotel_summary_options["hotels"]
                try:
                    for idx1, _ in enumerate(data_hotels[0:]):
                        DOMAIN = "https://www.hilton.com/en/"
                        locator_domain = DOMAIN
                        ln = _["name"]
                        location_name = ln if ln else MISSING
                        pu = _["facilityOverview"]["homeUrl"]
                        page_url = pu if pu else MISSING

                        a = _["address"]
                        sta = a["addressLine1"]
                        street_address = sta if sta else MISSING
                        city = a["city"] if a["city"] else MISSING
                        state = a["state"] if a["state"] else MISSING

                        pc = a["postalCode"]
                        zip_postal = pc if pc else MISSING

                        country_code = a["country"] if a["country"] else MISSING
                        logger.info(
                            f"[{idx}][{idx1}] | {country_name} | {country_link}"
                        )
                        store_number = _["ctyhocn"] if _["ctyhocn"] else MISSING
                        lat = _["localization"]["coordinate"]["latitude"]
                        latitude = lat if lat else MISSING

                        lng = _["localization"]["coordinate"]["longitude"]
                        longitude = lng if lng else MISSING

                        ph = _["contactInfo"]["phoneNumber"]
                        phone = ph if ph else MISSING

                        lt = _["brandCode"]
                        location_type = lt if lt else MISSING
                        hours_of_operation = MISSING
                        raw_address = a["addressFmt"]
                        raw_address = raw_address if raw_address else MISSING

                        item = SgRecord(
                            locator_domain=locator_domain,
                            page_url=page_url,
                            location_name=location_name,
                            street_address=street_address,
                            city=city,
                            state=state,
                            zip_postal=zip_postal,
                            country_code=country_code,
                            store_number=store_number,
                            phone=phone,
                            location_type=location_type,
                            latitude=latitude,
                            longitude=longitude,
                            hours_of_operation=hours_of_operation,
                            raw_address=raw_address,
                        )
                        sgw.write_row(item)
                except Exception as e:
                    logger.info(
                        f"Please fix this >> {e} | {country_name} | {country_link} | data_JSON: {data_json}"
                    )
    except Exception as e:
        logger.info(
            f"Please fix this >> {e} | {country_name} | {country_link} | data_JSON: {data_json}"
        )


def gen_countries(session):
    url = "https://www.hilton.com/en/locations/"
    headers = {
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36"
    }
    main = session.get(url, headers=headers)
    soup = b4(main.text, "lxml")
    countries = []
    data = soup.find_all(
        "div",
        {
            "id": lambda x: x and "location-tab-panel-" in x,
            "aria-labelledby": lambda x: x and "location-tab" in x,
            "role": "tabpanel",
            "tabindex": True,
            "class": True,
        },
    )
    for alist in data:
        links = alist.find_all("a")
        for link in links:
            countries.append(
                {
                    "text": link.text,
                    "link": link["href"].replace("https", "http"),
                    "complete": False,
                }
            )
    return countries


def get_city_province(num, country_name, country_link):
    city_or_province_list = []
    r_city = get_response(num, country_name, country_link)
    cities = r_city.json()
    if cities is not None:
        hotel_summary_options = cities["data"]["locationPage"]["hotelSummaryOptions"]
        data_hotels = hotel_summary_options["hotels"]
        city_interlinks = cities["data"]["locationPage"]["location"]["interlinks"]
        logger.info(f"{country_name} : {len(data_hotels)}")

        existing = {}
        existing["link"] = country_link
        existing["text"] = country_name
        existing["complete"] = False
        logger.info(f"store count type: {type(len(data_hotels))}")
        if len(data_hotels) == 150:
            logger.info("It returns 150 items that means it has more than 150 stores")
            for city_ilink in city_interlinks:
                d_new = {}
                city_path = "http://www.hilton.com/en/" + city_ilink["uri"]
                d_new["link"] = city_path
                d_new["text"] = country_name
                d_new["complete"] = False
                d_new["city_name"] = city_ilink["name"]
                city_or_province_list.append(d_new)
            city_or_province_list.append(existing)
        else:
            city_or_province_list.append(existing)

    return city_or_province_list


def get_cities_for_cn_gb_us(countries):
    cities_list = []
    for num, country_n_url in enumerate(countries):
        country_name = country_n_url["text"]
        country_link = country_n_url["link"]
        for dnum, i in enumerate(highly_dense_state_or_country_list[0:]):
            if i["c_or_s_name"].lower() in country_name.lower():
                city_province = get_city_province(num, country_name, country_link)
                cities_list.extend(city_province)
            else:
                cities_list.append(country_n_url)

    return cities_list


def fetch_data(sgw: SgWriter):
    with SgRequests(verify_ssl=False, timeout_config=300) as session:
        countries = gen_countries(session)
        sub_city_or_state = get_cities_for_cn_gb_us(countries)
        sub_city_or_state = [
            dict(t) for t in {tuple(d.items()) for d in sub_city_or_state}
        ]

        logger.info(f"after adding sub city or state: {sub_city_or_state}")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = []
            task = [
                executor.submit(fetch_records, idx, country_n_url, sgw)
                for idx, country_n_url in enumerate(sub_city_or_state[0:])
            ]
            tasks.extend(task)
            for future in as_completed(tasks):
                future.result()


def scrape():
    logger.info("Started")
    with SgWriter(
        SgRecordDeduper(
            SgRecordID(
                {
                    SgRecord.Headers.STORE_NUMBER,
                    SgRecord.Headers.PAGE_URL,
                    SgRecord.Headers.STREET_ADDRESS,
                    SgRecord.Headers.LATITUDE,
                    SgRecord.Headers.LONGITUDE,
                }
            )
        )
    ) as writer:
        fetch_data(writer)
    logger.info("Finished")


if __name__ == "__main__":
    scrape()
