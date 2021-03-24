from sgrequests import SgRequests
from sglogging import sglog
from sgselenium import SgChrome
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import csv

logzilla = sglog.SgLogSetup().get_logger("smart_com__gb__en")


def write_output(data):
    with open("data.csv", mode="w", newline="", encoding="utf8") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
        writer.writerow(
            [
                "locator_domain",
                "page_url",
                "location_name",
                "street_address",
                "city",
                "state",
                "zip",
                "country_code",
                "store_number",
                "phone",
                "location_type",
                "latitude",
                "longitude",
                "hours_of_operation",
            ]
        )
        # Body
        temp_list = []  # ignoring duplicates
        for row in data:
            comp_list = [
                row[1].strip(),
                row[2].strip(),
                row[3].strip(),
                row[4].strip(),
                row[5].strip(),
                row[6].strip(),
                row[8].strip(),
                row[10].strip(),
                row[11],
            ]
            if comp_list not in temp_list:
                temp_list.append(comp_list)
                writer.writerow(row)


def para(tup):
    headers = tup[1]
    session = SgRequests()
    k = tup[0]
    url = "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields=*&whiteList="
    son = session.get(url + k["baseInfo"]["externalId"], headers=headers).json()
    k = son
    return k


def get_data_using_company_id(cid):
    headers = cid[1]
    session = SgRequests()
    k = cid[0]
    url = "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields=*&whiteList="
    r_cid = session.get(url + str(k), headers=headers).json()
    return r_cid


def specialheaders():

    url = "https://www.mercedes-benz.co.uk/passengercars/mercedes-benz-cars/dealer-locator.html"

    headers = {}
    headers["x-apikey"] = ""
    headers[
        "User-Agent"
    ] = "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36"

    with SgChrome() as driver:
        driver.get(url)
        try:
            accept = WebDriverWait(driver, 50).until(
                EC.visibility_of_element_located(
                    (By.XPATH, '//*[@id="uc-btn-accept-banner"]')
                )
            )
            driver.execute_script("arguments[0].click();", accept)
        except Exception:
            headers["x-apikey"] = ""

        logzilla.info("Banner clicked with SUCCESS")
        driver.switch_to.frame("dlc-cont")
        logzilla.info("switch_to frame with SUCCESS")

        byname_xpath = '//button[text()="Search by name"]'
        byname = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.XPATH, byname_xpath))
        )

        driver.execute_script("arguments[0].click();", byname)
        logzilla.info("By Name search clicked with SUCCESS")
        sbar = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="mb-dl-spa"]/div/section[2]/div/form/div/input')
            )
        )

        logzilla.info("Before sending Benz Key with SUCCESS")
        sbar.send_keys("Benz")
        logzilla.info("After sending Benz Key with SUCCESS")

        dealer_xpath = '//span[@class="dl-dealers-search__submit--label"]'
        dealer = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.XPATH, dealer_xpath))
        )

        dealer = WebDriverWait(driver, 50).until(
            EC.visibility_of_element_located((By.XPATH, dealer_xpath))
        )

        driver.execute_script("arguments[0].click();", dealer)
        logzilla.info("dealer clicked with SUCCESS")

        for r in driver.requests:
            if "/dlc/dms/v2/dealers/search" in r.path:
                logzilla.info("[/dlc/dms/v2/dealers/search] found in %s" % r.path)
                try:
                    headers["x-apikey"] = r.headers["x-apikey"]
                except Exception:
                    try:
                        headers["x-apikey"] = r.response.headers["x-apikey"]
                    except Exception:
                        headers["x-apikey"] = headers["x-apikey"]
        logzilla.info("x-apikey: %s" % headers["x-apikey"])

    return headers


def determine_brand(k):
    brands = []
    for i in k["brands"]:
        brands.append(
            str(i["brand"]["name"]) + str("(" + str(i["brand"]["code"]) + ")")
        )
    logzilla.info(" brands: %s" % brands)
    return ", ".join(brands)


def determine_smart(brand):
    return "mart" in brand or "SMT" in brand


def determine_hours(k, brand, which):
    hours = "<MISSING>"
    h = []
    if which != "LITERALLYANYTHING" and which != "SUPERLITERALLYANYTHING":
        try:
            for i in k["functions"]:
                if (
                    i["brandCode"] == brand
                    and i["activityCode"] == which
                    and len(h) == 0
                ):
                    try:
                        for j in list(i["openingHours"]):
                            if i["openingHours"][j]["open"]:
                                h.append(
                                    str(j)
                                    + ": "
                                    + str(
                                        i["openingHours"][j]["timePeriods"][0]["from"]
                                    )
                                    + "-"
                                    + str(i["openingHours"][j]["timePeriods"][0]["to"])
                                )
                            else:
                                h.append(str(j) + ": Closed")
                    except Exception:
                        continue
            if len(h) == 0:
                hours = determine_hours(k, brand, "LITERALLYANYTHING")
            else:
                return "; ".join(h)
        except Exception:
            return hours

    if which == "LITERALLYANYTHING":
        for i in k["functions"]:
            if i["brandCode"] == brand and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            hours = determine_hours(k, brand, "SUPERLITERALLYANYTHING")
        else:
            return "; ".join(h)

    if which == "SUPERLITERALLYANYTHING":
        for i in k["functions"]:
            if hours == "<MISSING>" and len(h) == 0:
                try:
                    for j in list(i["openingHours"]):
                        if i["openingHours"][j]["open"]:
                            h.append(
                                str(j)
                                + ": "
                                + str(i["openingHours"][j]["timePeriods"][0]["from"])
                                + "-"
                                + str(i["openingHours"][j]["timePeriods"][0]["to"])
                            )
                        else:
                            h.append(str(j) + ": Closed")
                except Exception:
                    continue
        if len(h) == 0:
            return hours
        else:
            return "; ".join(h)

    return hours


def fix_comma(x):
    h = []
    try:
        x = x.split(",")
        for i in x:
            st = i.strip()
            if len(st) >= 1:
                h.append(st)
        h = ", ".join(h)
    except Exception:
        h = x

    return h


def fetch_data():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.66 Safari/537.36",
        "x-apikey": "45ab9277-3014-4c9e-b059-6c0542ad9484",
    }

    headers = specialheaders()
    resultsList = (
        "https://api.corpinter.net/dlc/dms/v2/dealers/search?marketCode=GB&fields="
    )
    session = SgRequests()
    results = session.get(resultsList, headers=headers).json()
    search_space = [[i, headers] for i in results["results"]]

    data_list = []
    items = []
    for i in search_space:
        data_from_para = para(i)
        company_id = data_from_para["results"][0]["baseInfo"]["companyId"]
        company_id_based_search = (company_id, headers)
        data_details = get_data_using_company_id(company_id_based_search)
        data = data_details["results"]
        data_list.append(data)

    for d in data_list:
        locator_domain = "https://www.mercedes-benz.co.uk/"
        page_url = "<MISSING>"
        if "website" in d[0]["contact"]:
            page_url = d[0]["contact"]["website"]
        else:
            page_url = "<MISSING>"
        location_name = d[0]["baseInfo"]["name1"] or "<MISSING>"
        sa = d[0]["address"]
        if "line1" in sa:
            l1 = sa["line1"]
        else:
            l1 = ""
        if "line2" in sa:
            l2 = sa["line2"]
        else:
            l2 = ""
        l = l1 + ", " + l2
        l = fix_comma(l)
        street_address = l or "<MISSING>"
        city = d[0]["address"]["city"] or "<MISSING>"
        if "region" in d[0]["address"]["region"]:
            state1 = d[0]["address"]["region"]["region"]
        else:
            state1 = ""

        if "subRegion" in d[0]["address"]["region"]:
            state2 = d[0]["address"]["region"]["subRegion"]
        else:
            state2 = ""

        if state1 and state2:
            state = state1 + ": " + state2
        elif state1 and not state2:
            state = state1
        elif state2 and not state1:
            state = state2
        else:
            state = "<MISSING>"

        zip = d[0]["address"]["zipcode"] or "<MISSING>"
        country_code = d[0]["address"]["country"] or "<MISSING>"
        store_number = d[0]["baseInfo"]["externalId"] or "<MISSING>"
        if "phone" in d[0]["contact"]:
            phone = d[0]["contact"]["phone"] or "<MISSING>"
        else:
            phone = "<MISSING>"
        location_type = determine_brand(d[0])
        if "latitude" in d[0]["address"]:
            latitude = d[0]["address"]["latitude"]
        else:
            latitude = "<MISSING>"

        if "longitude" in d[0]["address"]:
            longitude = d[0]["address"]["longitude"]
        else:
            longitude = "<MISSING>"

        hours_of_operation = determine_hours(d[0], "SMT", "SALES")
        row = [
            locator_domain,
            page_url,
            location_name,
            street_address,
            city,
            state,
            zip,
            country_code,
            store_number,
            phone,
            location_type,
            latitude,
            longitude,
            hours_of_operation,
        ]
        items.append(row)
    return items


def scrape():
    data = fetch_data()
    write_output(data)


if __name__ == "__main__":
    scrape()
