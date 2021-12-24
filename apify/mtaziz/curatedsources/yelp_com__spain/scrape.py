from sgscrape.sgrecord import SgRecord
from sglogging import SgLogSetup
from concurrent.futures import ThreadPoolExecutor, as_completed
from tenacity import retry, stop_after_attempt
import tenacity
from sgrequests import SgRequests
import json
import ssl
from lxml import html
import csv

ssl._create_default_https_context = ssl._create_unverified_context

logger = SgLogSetup().get_logger(logger_name="yelp_com")

MISSING = SgRecord.MISSING
MAX_WORKERS = 10
COUNTRY_TO_BE_CRAWLED = "Spain"

MAIN_CATEGORY_KEYWORDS = {
    "restaurants": "restaurants",
    "home_services": "homeservices",
    "auto_services": "auto",
    "local_services": "localservices",
}

headers_c = {
    "content-type": "application/json",
    "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36",
}

FIELDS = [
    "vk_id",
    "category",
    "site_id",
    "name",
    "lat",
    "lon",
    "street",
    "street_two",
    "locality",
    "region",
    "postal_code",
    "country",
    "telephone",
    "website",
    "url",
    "listed_review_count",
    "newest_review_date",
    "rating",
    "is_claimed_business",
    "hours_of_operation",
    "matched_category",
]


def write_output(data):
    with open("data.csv", mode="w", encoding="utf8", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        writer.writerow(FIELDS)
        for row in data:
            writer.writerow(row)


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response(url):
    with SgRequests() as http:
        r = http.get(url, headers=headers_c)
        try:
            if r.status_code == 200:
                logger.info(f"HTTP status code: {r.status_code} for {url}")
                return r
            raise Exception(f"Please fix {url}")
        except Exception as e:
            raise Exception(f"Please fix it {e} | {url}")


@retry(stop=stop_after_attempt(5), wait=tenacity.wait_fixed(5))
def get_response_custom(url):
    with SgRequests() as http:
        r = http.get(url, headers=headers_c)
        try:
            if r.status_code == 200:
                sel_retry = html.fromstring(r.text)
                data_raw = sel_retry.xpath(
                    '//script[contains(@type, "application/json") and contains(text(), "ROOT_QUERY")]/text()'
                )
                data_raw1 = "".join(data_raw)
                data_raw2 = data_raw1.split("<!--")[-1].split("-->")[0]
                data3 = data_raw2.replace("&quot;", '"')
                try:
                    data3_json = json.loads(data3)
                    if data3_json:
                        return r
                except Exception as e:
                    raise Exception(f"Retry-3: Please fix the issue {e} {url}")
            raise Exception(f"Retry-2: Please fix {url}")
        except Exception as e:
            raise Exception(f"Retry-1: Please fix it {e} | {url}")


def gen_main_cat_urls():
    main_cat_urls = []
    postcodes_madrid_list = [
        "28000",
        "28001",
        "28002",
        "28003",
        "28004",
        "28005",
        "28006",
        "28007",
        "28008",
        "28009",
        "28010",
        "28011",
        "28012",
        "28013",
        "28014",
        "28015",
        "28016",
        "28017",
        "28018",
        "28019",
        "28020",
        "28021",
        "28022",
        "28023",
        "28024",
        "28025",
        "28026",
        "28027",
        "28028",
        "28029",
        "28030",
        "28031",
        "28032",
        "28033",
        "28034",
        "28035",
        "28036",
        "28037",
        "28038",
        "28039",
        "28040",
        "28041",
        "28042",
        "28043",
        "28044",
        "28045",
        "28046",
        "28047",
        "28048",
        "28049",
        "28050",
        "28051",
        "28052",
        "28053",
        "28054",
        "28055",
        "28070",
        "28071",
        "28082",
        "28083",
        "28085",
        "28086",
        "28087",
        "28119",
        "28149",
        "28339",
        "28391",
        "28419",
        "28499",
        "28513",
        "28520",
        "28660",
        "28668",
        "28669",
        "28679",
        "28790",
        "28798",
        "28819",
        "28851",
        "28925",
    ]
    for k, v in MAIN_CATEGORY_KEYWORDS.items():
        for zidx, dzip in enumerate(postcodes_madrid_list[0:]):
            cat_url = f"https://www.yelp.com/search?cflt={v}&find_loc={dzip}%2C%20{COUNTRY_TO_BE_CRAWLED}"
            main_cat_urls.append(cat_url)
    logger.info(f"Total Search URLs: {len(main_cat_urls)}")
    return main_cat_urls


def get_paginated_urls(catnum, caturl):
    try:
        r = get_response(caturl)
        sel = html.fromstring(r.text)
        total_pages = sel.xpath(
            '//span[contains(@class, "css-1e4fdj9") and contains(text(), "of")]/text()'
        )
        total_pages = "".join(total_pages).replace("1 of ", "")
        logger.info(f"[{catnum}] total_pages: {total_pages}")
        if not total_pages:
            return
        else:
            page_nums_urls = [
                f"{caturl}&start={i*10}" for i in range(0, int(total_pages))
            ]
            return page_nums_urls
    except Exception as e:
        logger.info(f"Please fix {e} at {caturl}")


def get_paginated_urls_for_all_main_cats(mcurls):
    paginated_urls_list = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(get_paginated_urls, catnum, caturl)
            for catnum, caturl in enumerate(mcurls[0:])
        ]
        for future in as_completed(futures):
            paginated_future_result = future.result()
            if paginated_future_result or paginated_future_result is not None:
                paginated_urls_list.extend(paginated_future_result)
    return paginated_urls_list


def get_store_urls_from_paginated_pages(mnum, paginated_url):
    try:
        r1 = get_response(paginated_url)
        logger.info(f"[{mnum}] Pulling store URLs from paginated URLs {paginated_url}")
        text1 = r1.text
        sel1 = html.fromstring(text1)
        store_urls = sel1.xpath('//a[contains(@class, "css-1422juy")]/@href')
        store_urls = [i for i in store_urls if "/biz/" in i]
        store_urls = [f"https://www.yelp.com{i}" for i in store_urls]
        return store_urls
    except Exception as e:
        logger.info(f"Please fix paginated url {e} at {paginated_url}")


def get_store_urls(mcp_urls):
    store_urls_all = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = [
            executor.submit(get_store_urls_from_paginated_pages, mnum, paginated_url)
            for mnum, paginated_url in enumerate(mcp_urls[0:])
        ]
        for future in as_completed(futures):
            fut_result = future.result()
            store_urls_all.extend(fut_result)
    store_urls_all = list(set(store_urls_all))
    return store_urls_all


def fetch_records(sunum, surl):
    vk_id = MISSING
    category = ""
    site_id = ""
    name = ""
    lat = ""
    lon = ""
    street = ""
    street_two = ""
    locality = ""
    region = ""
    postal_code = ""
    country = ""
    telephone = ""
    website = ""
    url = ""
    listed_review_count = ""
    newest_review_date = ""
    rating = ""
    is_claimed_business = ""
    hours_of_operation = ""
    matched_category = ""
    try:
        logger.info(f"[{sunum}] Pulling the data from the store {surl}")
        r_store = get_response_custom(surl)

        text_store = r_store.text
        sel_store = html.fromstring(text_store, "lxml")
        local_business_data = "".join(
            sel_store.xpath(
                '//script[contains(@type, "application/ld+json") and contains(text(), "telephone")]/text()'
            )
        )
        local_business_data = json.loads(local_business_data)
        site_id = "".join(sel_store.xpath('//meta[@name="yelp-biz-id"]/@content'))
        name = local_business_data["name"]
        name = name if name else MISSING
        street = local_business_data["address"]["streetAddress"]
        if street:
            try:
                street = ", ".join(street.split("\n"))
            except:
                street = MISSING
        else:
            street = MISSING

        street_two = ""
        street_two = street_two if street_two else MISSING

        locality = local_business_data["address"]["addressLocality"]
        locality = locality if locality else MISSING

        region = local_business_data["address"]["addressRegion"]
        region = region if region else MISSING

        postal_code = local_business_data["address"]["postalCode"]
        postal_code = postal_code if postal_code else MISSING

        country = local_business_data["address"]["addressCountry"]
        country = country if country else MISSING

        telephone = local_business_data["telephone"]
        telephone = telephone if telephone else MISSING
        logger.info(f"[{sunum}] Tel: {telephone}]")

        # Review Count ( Total Reviews )
        review_count_xpath = (
            '//span[contains(text(), "review") and contains(@class, "css-1yy")]/text()'
        )
        try:
            rc = "".join(sel_store.xpath(review_count_xpath))
            if rc:
                listed_review_count = (
                    rc.replace("reviews", "").replace("review", "").strip()
                )
                logger.info(f"[{sunum}] {listed_review_count}")
            else:
                listed_review_count = MISSING
        except:
            try:
                lrc = local_business_data["aggregateRating"]["reviewCount"]
                listed_review_count = lrc if lrc else MISSING
            except Exception as e:
                listed_review_count = MISSING
                logger.info(f"Fix Xpath {e} {surl}")

        try:
            nrd = local_business_data["review"][0]["datePublished"]
            newest_review_date = nrd if nrd else MISSING
        except Exception as e:
            logger.info(f"Fix Newest review date: {e}")
            newest_review_date = MISSING

        try:
            rating = local_business_data["aggregateRating"]["ratingValue"]
            rating = rating if rating else MISSING
        except:
            try:
                star_rating_xpath = '//div[contains(@aria-label, "star rating") and contains(@class, "i-stars--large")]/@aria-label'
                star_rating = "".join(sel_store.xpath(star_rating_xpath))
                if star_rating:
                    rating = star_rating.replace("star rating", "").strip()
                else:
                    rating = MISSING
            except:
                rating = MISSING

        web = "".join(
            sel_store.xpath(
                '//div[p[contains(text(), "Business website")]]/p/following-sibling::p/a/text()'
            )
        )
        if web:
            website = web
        else:
            website = MISSING

        url = r_store.url
        yelp_frontend_data2 = sel_store.xpath(
            '//script[contains(@type, "application/json") and contains(text(), "ROOT_QUERY")]/text()'
        )
        yelp_frontend_data3 = "".join(yelp_frontend_data2)
        yelp_frontend_data3 = yelp_frontend_data3.split("<!--")[-1].split("-->")[0]
        data3 = yelp_frontend_data3.replace("&quot;", '"')
        data3_json = json.loads(data3)
        gmap_url_list = []
        hoo = []
        matched_categories_list = []
        for k, v in data3_json.items():
            if "regularHoursMergedWithSpecialHoursForCurrentWeek" in k:
                operation_hours = data3_json[k]
                time_json = "".join(operation_hours["regularHours"]["json"])
                if time_json is not None or not time_json:
                    days_of_week = operation_hours["dayOfWeekShort"]
                    time_and_days_of_week = f"{days_of_week} {time_json}"
                    hoo.append(time_and_days_of_week)
                else:
                    hoo = []

            if "useConsumerClaimability" in k:
                is_claimed = data3_json[k]
                is_claimed_biz = is_claimed["isClaimed"]
                logger.info(f"is_claimed_biz: {is_claimed_biz}")
            if "categories.0.root" in k:
                categories_root = data3_json[k]
                if categories_root["title"] is None or not categories_root:
                    category = MISSING
                else:
                    category = categories_root["title"]

            if "categories.0.ancestry" in k:
                categories_ancestry = data3_json[k]
                cat_an = categories_ancestry["alias"]
                matched_categories_list.append(cat_an)
            if ".map" in k:
                gmap_url = data3_json[k]["src"].replace("&#x2F;", "/")
                gmap_url_list.append(gmap_url)
        try:
            gmap = gmap_url_list[0]
            lat = gmap.split("png%7C")[-1].split("&amp;")[0].split("%2C")[0]
            lon = gmap.split("png%7C")[-1].split("&amp;")[0].split("%2C")[1]
            if lat == "0":
                lat = "<MISSING>"
            if lon == "0":
                lon = "<MISSING>"
            if "&amp" in lon:
                lon = lon.split("&amp")[0]
            if "&amp" in lat:
                lat = lat.split("&amp")[0]
            if not lat:
                lat = MISSING
            if not lon:
                lon = MISSING
        except:
            try:
                gmap = gmap_url_list[0]
                lat = gmap.split("center=")[-1].split("&amp;markers")[0].split("%2C")[0]
                lon = gmap.split("center=")[-1].split("&amp;markers")[0].split("%2C")[1]
                if "&amp" in lon:
                    lon = lon.split("&amp")[0]

                if "&amp" in lat:
                    lat = lat.split("&amp")[0]
                if not lat:
                    lat = MISSING
                if not lon:
                    lon = MISSING
                if "%7C" in lon:
                    lat = lon.split("%7C")[0]
                    lon = lon.split("%7C")[1]
            except:
                lat = MISSING
                lon = MISSING

        if is_claimed_biz is True:
            is_claimed_business = "1"

        if is_claimed_biz is False:
            is_claimed_business = "0"

        if hoo:
            hours_of_operation = "; ".join(hoo)
        else:
            hours_of_operation = MISSING
        if matched_categories_list:
            matched_category = ", ".join(matched_categories_list)
        else:
            matched_category = MISSING
        cat = " ".join(category.split())
        if cat:
            category = category
        else:
            category = MISSING
        row = [
            vk_id,
            category,
            site_id,
            name,
            lat,
            lon,
            street,
            street_two,
            locality,
            region,
            postal_code,
            country,
            telephone,
            website,
            url,
            listed_review_count,
            newest_review_date,
            rating,
            is_claimed_business,
            hours_of_operation,
            matched_category,
        ]
        return row
    except Exception as e:
        logger.info(f"Please fix Expath or JSON {e} | {surl}")


def fetch_data():

    # Step 1 - generate main category based URLs based on Country and main category
    main_caturls = gen_main_cat_urls()
    logger.info("main categories urls crawlering done!")

    # Step 2 - get category based paginated URLs
    paginated_urls = get_paginated_urls_for_all_main_cats(main_caturls[0:])

    # Step 3 - get store urls
    store_urls = get_store_urls(paginated_urls)

    logger.info(f"Total Store Count: {len(store_urls)}")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        tasks = []
        task = [
            executor.submit(fetch_records, sunum, surl)
            for sunum, surl in enumerate(store_urls[0:])
        ]
        tasks.extend(task)
        for future in as_completed(tasks):
            record = future.result()
            if record is not None:
                yield record


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    logger.info("Scrape started")
    scrape()
    logger.info("Scrape Finished")
