from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
import csv
from webdriver_manager.chrome import ChromeDriverManager
from sglogging import sglog

log = sglog.SgLogSetup().get_logger(logger_name="carehome")


def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                    if "longitude" in json.loads(html_string[start : end + 1]).keys():
                        break

                except Exception:
                    pass
        count = count + 1

    return json_objects


def reset_sessions(data_url):
    s = SgRequests()

    driver = SgChrome(
        is_headless=True, executable_path=ChromeDriverManager().install()
    ).driver()
    driver.get(data_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                driver.quit()
                return [s, headers, response_text]

        except Exception:
            continue


data_url = "https://www.carehome.co.uk/"
new_sess = reset_sessions(data_url)

s = new_sess[0]
headers = new_sess[1]
response_text = new_sess[2]

soup = bs(response_text, "html.parser")

strong_tags = soup.find(
    "div", attrs={"class": "row", "style": "margin-bottom:30px"}
).find_all("strong")
country_urls = []
location_urls = []
for strong_tag in strong_tags:
    a_tag = strong_tag.find("a")
    url = a_tag["href"]

    if "searchcountry" in url:
        country_urls.append(url)

x = 0
for country_url in country_urls:

    response = s.get(country_url, headers=headers)
    response_text = response.text
    if len(response_text.split("div")) > 2:
        pass
    else:
        new_sess = reset_sessions(country_url)

        s = new_sess[0]
        headers = new_sess[1]
        response_text = new_sess[2]

    soup = bs(response_text, "html.parser")
    search_length = int(
        soup.find_all("a", attrs={"class": "page-link"})[-2].text.strip()
    )

    count = 1
    while count < search_length + 1:
        search_url = country_url + "/startpage/" + str(count)
        response = s.get(search_url, headers=headers)
        response_text = response.text
        log.info(search_url)
        if len(response_text.split("div")) > 2:
            pass
        else:
            y = 0
            while True:
                y = y + 1
                log.info("page_url_fail: " + str(y))
                try:
                    new_sess = reset_sessions(search_url)

                    s = new_sess[0]
                    headers = new_sess[1]
                    response_text = new_sess[2]
                    break
                except Exception:
                    continue

        soup = bs(response_text, "html.parser")
        div_tags = soup.find_all("div", attrs={"class": "col-sm-9 col-xs-12"})
        for div_tag in div_tags:
            try:
                location_url = div_tag.find(
                    "a", attrs={"style": "font-weight:bold;font-size:28px"}
                )["href"]
            except Exception:
                a_tags = div_tag.find_all("a")
                for a_tag in a_tags:
                    try:
                        location_url = a_tag["href"]
                    except Exception:
                        pass

            if location_url in location_urls:
                pass
            else:
                location_urls.append(location_url)
        count = count + 1

x = 0
with open("data.csv", mode="w") as output_file:
    writer = csv.writer(
        output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
    )
    writer.writerow(
        [
            "locator_domain",
            "page_url",
            "location_name",
            "location_type",
            "store_number",
            "street_address",
            "city",
            "state",
            "zip",
            "country_code",
            "latitude",
            "longitude",
            "phone",
            "hours_of_operation",
        ]
    )
    for location_url in location_urls:
        x = x + 1
        response = s.get(location_url, headers=headers)
        response_text = response.text
        log.info("URL " + str(x) + "/" + str(len(location_urls)))
        log.info(location_url)
        if len(response_text.split("div")) > 2:
            pass
        else:
            y = 0
            while True:
                y = y + 1
                log.info("location_url_fail: " + str(y))
                try:
                    new_sess = reset_sessions(location_url)

                    s = new_sess[0]
                    headers = new_sess[1]
                    response_text = new_sess[2]
                    break
                except Exception:
                    continue

        soup = bs(response_text, "html.parser")

        locator_domain = "carehome.co.uk"
        page_url = location_url
        location_name = soup.find("h1", attrs={"class": "mb-0 card-title"}).text.strip()
        if len(location_name.split("\n")) > 1:
            continue

        address_parts = soup.find("meta", attrs={"property": "og:title"})["content"].split(
            ","
        )
        address = address_parts[1].strip()
        city = address_parts[-2].strip()
        state_zipp_parts = address_parts[-1].split(" |")[0].split(" ")
        state_parts = state_zipp_parts[:-2]
        state = ""
        for part in state_parts:
            state = state + part + " "
        state = state.strip().replace("County ", "")

        zipp = state_zipp_parts[-2] + " " + state_zipp_parts[-1]

        country_code = "UK"
        store_number = location_url.split("/")[-1]
    
        try:
            phone_link = soup.find("button", attrs={"id": "brochure_phone"})["href"]
            phone_response = s.get(phone_link, headers=headers).text
            response_soup = bs(phone_response, "html.parser")
            phone = (
                response_soup.find("div", attrs={"class": "contacts_telephone"})
                .find("a")
                .text.strip()
            )
        except Exception:
            phone = "<MISSING>"

        geo_json = extract_json(response_text.split('geo":')[1].split("reviews")[0])[0]
        latitude = geo_json["latitude"]
        longitude = geo_json["longitude"]
        hours = "<MISSING>"

        try:
            location_type = [
                item.strip()
                for item in soup.find("div", attrs={"class": "row profile-row"})
                .text.strip()
                .split("Care Provided")[1]
                .split("Type of Service")[1]
                .split("\n")
                if len(item) > 2
            ][0] + [item.strip()
                for item in soup.find("div", attrs={"class": "row profile-row"})
                .text.strip()
                .split("Care Provided")[1]
                .split("Type of Service")[1]
                .split("\n")
                if len(item) > 2
            ][1]

        except Exception:
            location_type = "<MISSING>"

        row = [locator_domain, page_url, location_name, location_type, store_number, address, city, state, zipp, country_code, latitude, longitude, phone, hours]
        
        writer.writerow(row)
        
        if x == 100:
            break
