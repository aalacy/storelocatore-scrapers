from sglogging import sglog


from sgrequests import SgRequests
from bs4 import BeautifulSoup as b4

import json

import asyncio
import httpx

import os


def set_proxies():
    if "PROXY_PASSWORD" in os.environ and os.environ["PROXY_PASSWORD"].strip():

        proxy_password = os.environ["PROXY_PASSWORD"]
        url = os.environ["PROXY_URL"] if "PROXY_URL" in os.environ else None
        proxy_url = url.format(proxy_password)
        proxies = {
            "http://": proxy_url,
        }
        return proxies
    else:
        return None


errors = []
proxies = set_proxies()
logzilla = sglog.SgLogSetup().get_logger(logger_name="Scraper")
chunk_size = 15  # concurrencu for asincyio


def sub_data(record):
    global errors
    soup = b4(record["response"], "lxml")
    record["response"] = ""
    try:
        variationData = json.loads(
            soup.find(
                "form",
                {
                    "class": lambda x: x
                    and all(i in x for i in ["variations_form", "cart"]),
                    "method": "post",
                    "action": True,
                    "data-product_variations": True,
                },
            )["data-product_variations"].strip()
        )
    except TypeError as e:
        variationData = None
        errors.append(str(str(record) + str(e)))
    record["domain"] = soup.find("div", {"class": "content-container"}).find("a")[
        "href"
    ]
    mainData = soup.find_all("div", {"class": "content-container"})
    data = [i.text.strip() for i in mainData[0].find_all("p")]

    try:
        for i in data:
            if "Location Count:" in str(i):
                record["LocationCount"] = i.split("Location Count:")[1].split(" ", 1)[0]
    except Exception as e:
        record["LocationCount"] = "ERROR" + str(data)
        errors.append(str(str(record) + str(e)))
    try:
        for i in data:
            if "locations " in str(i):
                record["LocationCountWhere"] = (
                    i.split("locations ")[1].replace("in", "").strip()
                )
    except Exception as e:
        record["LocationCountWhere"] = "ERROR" + str(data)
        errors.append(str(str(record) + str(e)))
    record["variationData"] = variationData
    try:
        for i in data:
            if "Last Updated:" in str(i):
                record["lastUpdated"] = i.split(":", 1)[1].replace(
                    "Updated every ", " cycle - "
                )
    except Exception as e:
        record["lastUpdated"] = "ERROR" + str(data)
        errors.append(str(str(record) + str(e)))
    record["parentChain"] = "<MISSING>"
    try:
        for i in data:
            if "Parent Chain" in str(i):
                record["parentChain"] = i.split(":", 1)[1].strip()
    except Exception as e:
        errors.append(str(str(record) + str(e)))
        pass
    record["parentChainURL"] = "<MISSING>"
    if record["parentChain"] != "<MISSING>":
        # insert codde to append href here.
        # what could've I possibly meant by that?!
        links = soup.find_all("a")
        for link in links:
            if record["parentChain"] in link.text:
                record["parentChainURL"] = link["href"]

    data = [i.text.strip() for i in mainData[1].find_all("p")]
    record["categories"] = "<MISSING>"
    try:
        for i in data:
            if "Categories" in str(i):
                record["categories"] = i.split(":", 1)[1].strip()
                record["categories"].replace("Secondary", " Secondary")
    except Exception as e:
        record["categories"] = "ERROR" + str(data)
        errors.append(str(str(record) + str(e)))

    try:
        for i in data:
            if "SIC" in str(i):
                record["SIC"] = i.split(":", 1)[1].strip()
    except Exception as e:
        record["SIC"] = "ERROR" + str(data)
        errors.append(str(str(record) + str(e)))
    try:
        for i in data:
            if "NAICS" in str(i):
                record["NAICS"] = i.split(":", 1)[1].strip()
    except Exception as e:
        record["NAICS"] = "ERROR:" + str(data)
        errors.append(str(str(record) + str(e)))
    record["product_id"] = soup.find(
        "form",
        {
            "class": lambda x: x and all(i in x for i in ["variations_form", "cart"]),
            "method": "post",
            "action": True,
            "data-product_variations": True,
            "data-product_id": True,
        },
    )["data-product_id"]
    record["countryCount"] = 0
    if variationData:
        record["CountriesCountPrice"] = ", ".join(
            [
                str(
                    "{"
                    + str(
                        '"country/region":"{}",\n"count":"{}",\n"sub-countries":"{}",\n"price":"{}",\n"sku":"{}",\n"variation_id":"{}"'.format(
                            i["attributes"]["attribute_pa_country"],
                            i["variation_description"]
                            .split("<strong>")[-1]
                            .split("</", 1)[0]
                            .strip(),
                            i["variation_description"]
                            .split("available from ")[-1]
                            .split("</", 1)[0]
                            .strip()
                            if "available from " in i["variation_description"]
                            else i["attributes"]["attribute_pa_country"],
                            i["display_price"],
                            i["sku"],
                            i["variation_id"],
                        )
                    )
                    + "}"
                )
                for i in variationData
            ]
        )
        for i in variationData:
            record["countryCount"] += len(
                i["variation_description"]
                .split("available from ")[-1]
                .split("</", 1)[0]
                .split(",")
                if "available from " in i["variation_description"]
                else "1"
            )

    else:
        record["CountriesCountPrice"] = '"Sorry, this product is unavailable."'
    record["CountriesCountPrice"] = "[\n" + record["CountriesCountPrice"] + "\n]"
    return record


def transform_data(soup):
    data = soup.find(
        "ul",
        {
            "class": lambda x: x
            and all(i in x for i in ["products", "clearfix", "products-1"])
        },
    ).find_all("li", {"class": lambda y: y and "post-" in y})
    for item in data:
        record = {}
        record["chainXYpage"] = item.find(
            "div", {"class": lambda x: x and "fusion-clean-product-image-wrapper" in x}
        ).find("a")["href"]
        moreData = item.find("div", {"class": "product-details"})
        record["brand"] = (
            moreData.find("span", {"class": "product-title"}).find("a").text.strip()
        )
        record["CountriesClaimed"] = ", ".join(
            [
                i.text.strip()
                for i in moreData.find("span", {"class": "flagicons"}).find_all(
                    "span", {"class": "cxytooltiptext"}
                )
            ]
        )
        yield record


def fetch_data():
    global errors

    async def getSubPage(record):
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        async with httpx.AsyncClient(
            proxies=proxies, headers=headers, timeout=None
        ) as client:
            try:
                response = await client.get(record["chainXYpage"], headers=headers)
                response = response.text
                record["response"] = response
                return record
            except Exception as e:
                errors.append(str(str(record) + str(e)))

    async def search(task_list):
        z = await asyncio.gather(*task_list)
        return z

    IterUrl = "https://chainxy.com/chains/page/{}/"
    breaker = "his Page Could Not Be Found"
    pagination = 1
    sub_searches = []
    with SgRequests() as session:
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
        }
        while True:
            response = session.get(IterUrl.format(pagination), headers=headers).text
            if breaker in response:
                break
            soup = b4(response, "lxml")
            for rec in transform_data(soup):
                sub_searches.append(rec)

            logzilla.info(f"Grabbed {IterUrl.format(pagination)}")
            pagination += 1

    maxZ = len(sub_searches)
    logzilla.info(
        f"Finished grabbing {pagination-1} pages. Preparing to make {maxZ} more visits"
    )  # noqa

    task_list = []
    while sub_searches:
        data = None
        if len(task_list) == chunk_size:
            data = asyncio.run(search(task_list))
            task_list = []
            try:
                task_list.append(getSubPage(sub_searches.pop(0)))
            except IndexError:
                sub_searches = None
        else:
            try:
                task_list.append(getSubPage(sub_searches.pop(0)))
                continue
            except IndexError:
                data = asyncio.run(search(task_list))
                sub_searches = None
        if data:
            for rec in data:
                try:
                    record = sub_data(rec)
                    yield record
                except Exception as e:
                    errors.append(str(str(rec) + str(e)))

        remaining = len(sub_searches)
        if remaining == 0:
            remaining = 1
        progress = str(round(100 - (remaining / maxZ * 100), 2)) + "%"
        logzilla.info(f"progress: {progress} | Concurrency: {chunk_size}\n")
    if len(task_list) != 0:
        data = asyncio.run(search(task_list))
        for rec in data:
            try:
                record = sub_data(rec)
                yield record
            except Exception as e:
                errors.append(str(str(rec) + str(e)))


def scrape():
    with open("data.csv", mode="w", encoding="utf-8") as file:
        header = '"ChainXY_URL","brand_name","SIC","NAICS","product_id","variation_data","location_count_country","location_count_for_country","which_countries_crawled","how_many_countries","last_updated","categories","brand_domain","countries_counts_prices","parent_chain","parent_chain_URL","Variation?"'
        file.write(header)
        for rec in fetch_data():
            ChainXY_URL = str(rec["chainXYpage"]).replace('"', "'")
            brand_name = str(rec["brand"]).replace('"', "'")
            try:
                SIC = str(rec["SIC"]).replace('"', "'")
            except KeyError:
                SIC = "<ERROR>"
            try:
                NAICS = str(rec["NAICS"]).replace('"', "'")
            except KeyError:
                NAICS = "<ERROR>"
            try:
                product_id = str(rec["product_id"]).replace('"', "'")
            except KeyError:
                product_id = "<ERROR>"
            try:
                variation_data = str(rec["variationData"]).replace('"', "'")
            except KeyError:
                variation_data = "<ERROR>"
            try:
                location_count_country = str(rec["LocationCount"]).replace('"', "'")
            except KeyError:
                location_count_country = "<ERROR>"
            try:
                location_count_for_country = str(rec["LocationCountWhere"]).replace(
                    '"', "'"
                )
            except KeyError:
                location_count_for_country = "<ERROR>"

            try:
                which_countries_crawled = str(rec["CountriesClaimed"]).replace('"', "'")
            except KeyError:
                which_countries_crawled = "<ERROR>"
            try:
                how_many_countries = str(rec["countryCount"]).replace('"', "'")
            except KeyError:
                how_many_countries = "<ERROR>"
            try:
                last_updated = str(rec["lastUpdated"]).replace('"', "'")
            except KeyError:
                last_updated = "<ERROR>"
            try:
                categories = str(rec["categories"]).replace('"', "'")
            except KeyError:
                categories = "<ERROR>"
            try:
                brand_domain = str(rec["domain"]).replace('"', "'")
            except KeyError:
                brand_domain = "<ERROR>"
            try:
                countries_counts_prices = str(rec["CountriesCountPrice"]).replace(
                    '"', "'"
                )
            except KeyError:
                countries_counts_prices = "<ERROR>"
            try:
                parent_chain = str(rec["parentChain"]).replace('"', "'")
            except KeyError:
                parent_chain = "<ERROR>"
            try:
                parent_chain_URL = str(rec["parentChainURL"]).replace('"', "'")
            except KeyError:
                parent_chain_URL = "<ERROR>"
            uglystring = '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","False"'.format(
                ChainXY_URL,
                brand_name,
                SIC,
                NAICS,
                product_id,
                variation_data,
                location_count_country,
                location_count_for_country,
                which_countries_crawled,
                how_many_countries,
                last_updated,
                categories,
                brand_domain,
                countries_counts_prices,
                parent_chain,
                parent_chain_URL,
            )
            file.write(str("\n" + uglystring.replace("\n", "").replace("\r", "")))
            if rec["variationData"]:
                for country in rec["variationData"]:
                    variation_data = str(country["sku"]).replace('"', "'")
                    location_count_for_country = str(
                        country["attributes"]["attribute_pa_country"]
                    ).replace('"', "'")
                    countries_counts_prices = str(country["display_price"]).replace(
                        '"', "'"
                    )
                    mainData = b4(country["variation_description"], "lxml")

                    location_count_country = str(
                        mainData.find_all("strong")[-1].text
                    ).replace('"', "'")
                    try:
                        which_countries_crawled = (
                            str(
                                country["variation_description"].split(
                                    "available from "
                                )[1]
                            )
                            .replace("</p>\n", "")
                            .replace('"', "'")
                        )
                    except Exception:
                        pass
                    uglystring = '"{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","{}","True"'.format(
                        ChainXY_URL,
                        brand_name,
                        SIC,
                        NAICS,
                        product_id,
                        variation_data,
                        location_count_country,
                        location_count_for_country,
                        which_countries_crawled,
                        how_many_countries,
                        last_updated,
                        categories,
                        brand_domain,
                        countries_counts_prices,
                        parent_chain,
                        parent_chain_URL,
                    )
                    file.write(
                        str("\n" + uglystring.replace("\n", "").replace("\r", ""))
                    )

    if len(errors) > 0:
        with open("errors.txt", mode="w", encoding="utf-8") as errorz:
            for error in errors:
                errorz.write(str(error))


if __name__ == "__main__":
    scrape()
