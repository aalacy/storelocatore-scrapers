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
from datetime import datetime
import dateutil.parser
import ssl

logger = SgLogSetup().get_logger(logger_name="hiltongardeninn3_hilton_com")
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


@retry(stop=stop_after_attempt(7), wait=tenacity.wait_fixed(20))
def get_response_redirect(urlnum, country, url_to_redirect):
    # There are some store URLs those may be redirected.
    # Path as a part of the payload, is formed from store URLs.
    # Since it's a POST request, the crawler is not able to automatically
    # get the redirected URL leading the Path to be different than redirected path.
    # This deals with such redirected store URLs.
    logger.info("Pulling response from to-be-redirected URL")
    with SgRequests(timeout_config=600, verify_ssl=False) as http:
        r_redir = http.get(url_to_redirect, headers=headers_c)
        try:
            if r_redir.status_code == 200:
                redir_url = r_redir.url
                logger.info(f"redirected URL: {redir_url}")
                path_per_country_or_state_redirect = str(redir_url).split("/en/")[-1]
                payload_redirect = {
                    "query": "query hotelSummaryOptions_locationPage($language: String!, $path: String!, $queryLimit: Int!, $currencyCode: String!, $distanceUnit: HotelDistanceUnit, $titleFormat: MarkdownFormatType!) {\n  locationPage(language: $language, path: $path) {\n    location {\n      interlinkTitle\n      interlinks {\n        uri\n        name\n      }\n      _id: uri\n      title(format: $titleFormat)\n      accessibilityTitle\n      meta {\n        pageTitle\n        description\n      }\n      name\n      brandCode\n      category\n      uri\n      globalBounds\n      breadcrumbs {\n        uri\n        name\n      }\n      about {\n        desc\n        headline\n        shortDesc\n      }\n      paths {\n        base\n      }\n    }\n    match {\n      address {\n        city\n        country\n        countryName\n        postalCode\n        state\n        stateName\n      }\n      geometry {\n        location {\n          latitude\n          longitude\n        }\n        bounds {\n          northeast {\n            latitude\n            longitude\n          }\n          southwest {\n            latitude\n            longitude\n          }\n        }\n      }\n      name\n      type\n    }\n    hotelSummaryOptions(distanceUnit: $distanceUnit, sortBy: distance) {\n      _hotels {\n        totalSize\n      }\n      bounds {\n        northeast {\n          latitude\n          longitude\n        }\n        southwest {\n          latitude\n          longitude\n        }\n      }\n      amenities {\n        id\n        name\n      }\n      amenityCategories {\n        name\n        id\n        amenityIds\n      }\n      brands {\n        code\n        name\n      }\n      hotels(first: $queryLimit) {\n        amenityIds\n        brandCode\n        ctyhocn\n        distance\n        distanceFmt\n        facilityOverview {\n          allowAdultsOnly\n          homeUrl\n        }\n        name\n        contactInfo {\n          phoneNumber\n        }\n        display {\n          open\n          openDate\n          preOpenMsg\n          resEnabled\n          resEnabledDate\n        }\n        disclaimers {\n          desc\n          type\n        }\n        address {\n          addressFmt\n          addressLine1\n          city\n          country\n          countryName\n          postalCode\n          state\n          stateName\n        }\n        localization {\n          currencyCode\n          coordinate {\n            latitude\n            longitude\n          }\n        }\n        masterImage(variant: searchPropertyImageThumbnail) {\n          altText\n          variants {\n            size\n            url\n          }\n        }\n        leadRate {\n          lowest {\n            rateAmount(currencyCode: $currencyCode)\n            rateAmountFmt(decimal: 0, strategy: trunc)\n            ratePlan {\n              ratePlanName\n              ratePlanDesc\n            }\n          }\n        }\n      }\n    }\n  }\n}\n",
                    "operationName": "hotelSummaryOptions_locationPage",
                    "variables": {
                        "path": path_per_country_or_state_redirect,
                        "language": "en",
                        "queryLimit": QUERY_LIMIT,
                        "currencyCode": "USD",
                        "titleFormat": "md",
                    },
                }
                logger.info(f"redirected path: {path_per_country_or_state_redirect}")
                r_redir_post = http.post(
                    API_ENDPOINT_URL,
                    data=json.dumps(payload_redirect),
                    headers=headers_c,
                )
                if r_redir_post.status_code == 200:
                    js_redir = r_redir_post.json()
                    hot_redir = js_redir["data"]["locationPage"]["hotelSummaryOptions"]
                    if (r_redir_post.status_code == 200 and hot_redir is not None) or (
                        r_redir_post.status_code == 200 and "errors" in js_redir
                    ):
                        logger.info("hot_redir is not None")
                        hot2 = js_redir["data"]["locationPage"]["hotelSummaryOptions"][
                            "hotels"
                        ]
                        if (r_redir_post.status_code == 200 and hot2 is not None) or (
                            r_redir_post.status_code == 200 and "errors" in js_redir
                        ):
                            logger.info(
                                f"Redirect POST HTTP Status Code: {r_redir_post.status_code}"
                            )
                            return r_redir_post
                        raise Exception(
                            f"{urlnum} : {redir_url} >> Temporary Error: {hot2}"
                        )
                    raise Exception(
                        f"{urlnum} : {redir_url} >> Temporary Error: {hot_redir}"
                    )
                raise Exception(
                    f"{urlnum} : {redir_url} >> Temporary Error: {r_redir_post.status_code}"
                )
        except Exception as e:
            raise Exception(f"{urlnum} : {url_to_redirect} >> Temporary Error: {e}")


@retry(stop=stop_after_attempt(10), wait=tenacity.wait_fixed(20))
def get_response(urlnum, country, url):
    path_per_country_or_state = url.split("/en/")[-1]
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
        logger.info(f"[{urlnum}] | {country} | Pulling from: {url}")
        r = http.post(API_ENDPOINT_URL, data=json.dumps(payload1), headers=headers_c)
        try:
            if r.status_code == 200:
                rtext = r.text
                if rtext is not None:
                    js = json.loads(rtext)
                    hot = js["data"]["locationPage"]["hotelSummaryOptions"]
                    redirect_path = js["data"]["locationPage"]["location"]["uri"]
                    if hot is None and path_per_country_or_state != redirect_path:
                        logger.info(
                            f"{path_per_country_or_state} not in {redirect_path}"
                        )
                        rr = get_response_redirect(urlnum, country, url)
                        return rr
                    else:
                        if (r.status_code == 200 and hot is not None) or (
                            r.status_code == 200 and "errors" in js
                        ):
                            hot2 = js["data"]["locationPage"]["hotelSummaryOptions"][
                                "hotels"
                            ]
                            if (r.status_code == 200 and hot2 is not None) or (
                                r.status_code == 200 and "errors" in js
                            ):
                                logger.info(f"HTTP Status Code: {r.status_code}")
                                return r
                            raise Exception(
                                f"{urlnum} : {url} >> Level 4 - Temporary Error: {r.status_code}"
                            )
                        raise Exception(
                            f"{urlnum} : {url} >> Level 3 - Temporary Error: {r.status_code}"
                        )
                raise Exception(
                    f"{urlnum} : {url} >> Level 3 - Temporary Error: {r.status_code}"
                )
            raise Exception(
                f"{urlnum} : {url} >> Level 1 - Temporary Error: {r.status_code}"
            )
        except Exception as e:
            logger.info(
                f"{urlnum} : {url} >> Level 0 - Temporary Error: {r.status_code}"
            )
            raise Exception(
                f"{urlnum} : {url} >> Level 0 - Temporary Error: {r.status_code} {e}"
            )


def fetch_records(idx, country_n_url, sgw: SgWriter):
    country_name = country_n_url["text"]
    country_link = country_n_url["link"]
    r = get_response(idx, country_name, country_link)
    data_json = r.json()
    if data_json["data"]["locationPage"] is None:
        return
    if not data_json["data"]["locationPage"]:
        return
    else:
        if "hotelSummaryOptions" not in data_json["data"]["locationPage"]:
            return
        else:
            hotel_summary_options = data_json["data"]["locationPage"][
                "hotelSummaryOptions"
            ]
            if hotel_summary_options is None:
                return
            if not hotel_summary_options:
                return
            data_hotels = hotel_summary_options["hotels"]
            if not data_hotels:
                return
            else:
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

                        hours_of_operation = MISSING

                        lt = _["brandCode"]
                        location_type = lt if lt else MISSING

                        # Coming Soon based on whether hotel is open or close
                        # Get the local time based on the system the crawler is running on
                        local_time = datetime.now(datetime.now().astimezone().tzinfo)

                        # Hotel open or close status refers False or True
                        open_or_close = _["display"]["open"]

                        # Open Date refers to the opening date.
                        # If this is None then nothing required to do
                        open_date = _["display"]["openDate"]
                        parsed_open_date = None
                        if open_date is not None and open_or_close is False:
                            parsed_open_date = dateutil.parser.parse(open_date)
                            if parsed_open_date.timestamp() > local_time.timestamp():
                                hours_of_operation = "Coming Soon"
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
    x = 0
    while True:
        x = x + 1
        try:
            r_city = get_response(num, country_name, country_link)
            cities = r_city.json()
            data_hotels = cities["data"]["locationPage"]["hotelSummaryOptions"][
                "hotels"
            ]
            city_interlinks = cities["data"]["locationPage"]["location"]["interlinks"]
            logger.info(f"{country_name} : {len(data_hotels)}")
            existing = {}
            existing["link"] = country_link
            existing["text"] = country_name
            existing["complete"] = False
            logger.info(f"store count type: {type(len(data_hotels))}")
            if len(data_hotels) == 150:
                logger.info(
                    "It returns 150 items that means it has more than 150 stores"
                )
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
            break
        except Exception as e:
            if x == 5:
                logger.info(f"Fix the issue: {e} | {country_name} | {country_link}")
            continue
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


def dedupe(texas_dup_test):
    s = set()
    texas_deduped = []
    for i in texas_dup_test:
        linkd = i["link"]
        if linkd not in s:
            texas_deduped.append(i)
        s.add(linkd)
    return texas_deduped


def fetch_data(sgw: SgWriter):
    with SgRequests(verify_ssl=False, timeout_config=300) as session:
        countries = gen_countries(session)
        logger.info("Pulling URLs those having more than 150 Stores")
        sub_city_or_state = get_cities_for_cn_gb_us(countries[0:])
        logger.info(f"Raw Count: {len(sub_city_or_state)} ")
        sub_city_or_state_deduped = dedupe(sub_city_or_state)
        for i_dict in sub_city_or_state_deduped:
            if "http://www.hilton.com/en/locations/swaziland/" in i_dict["link"]:
                sub_city_or_state_deduped.remove(i_dict)
        logger.info(f"After Deduplication Count: {len(sub_city_or_state_deduped)}")
        logger.info("Pulling city-province based finished")
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            tasks = []
            task = [
                executor.submit(fetch_records, idx, country_n_url, sgw)
                for idx, country_n_url in enumerate(sub_city_or_state_deduped[0:])
            ]
            tasks.extend(task)
            for future in as_completed(tasks):
                if future.result() is not None:
                    future.result()
                else:
                    continue


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
