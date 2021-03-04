import csv
from time import sleep
from random import randint
from sgrequests import SgRequests
from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim


session = SgRequests()


def write_output(data):
    with open("data.csv", mode="w", newline="") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )
        writer.writerow(
            [
                "locator_domain",
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
                "page_url",
            ]
        )
        for row in data:
            writer.writerow(row)


def working_url():
    sleep(randint(1, 5))
    url = ""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    locator_domain = "https://www.skyscanner.co.in"
    res = session.get(locator_domain, headers=headers)
    soup = BeautifulSoup(res.text, "html5lib")
    footer = soup.find(class_="FooterLinkList_FooterLinkList__38pf4")
    for link in footer.find_all("li"):
        if link.find("a").text == "Airports":
            url = link.find("a")["href"]
            sleep(randint(1, 5))
            res = session.get(url, headers=headers)
            soup = BeautifulSoup(res.text, "html5lib")
            table = soup.find(class_="sm_table sm_table_sections1")
            for row in table.find_all("tr"):
                if row.text == "Airports in Europe":
                    url = row.find("a")["href"]
                    url = locator_domain + url
                    sleep(randint(1, 5))
                    res = session.get(url, headers=headers)
                    soup = BeautifulSoup(res.text, "html5lib")
                    tables = soup.find(id="sm_airports_in_continent")
                    table = tables.find_all(class_="rounded_frame")[1]
                    for rows in table.find_all("tr"):
                        for row in rows:
                            if row.text == "Airports in the UK - United Kingdom":
                                url = row.find("a")["href"]
                                return locator_domain + url


def airports_list(link):
    url = link
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    url_list = []
    head_url = "https://www.skyscanner.co.in"
    sleep(randint(1, 5))
    res = session.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html5lib")
    airports_data = soup.find(class_="sm_table sm_table_sections3")
    for airport in airports_data.find_all("td"):
        try:
            if "airports" in airport.text:
                tail_url = airport.find("a").get("href")
                url = head_url + tail_url
                sleep(randint(1, 5))
                res = session.get(url, headers=headers)
                soup = BeautifulSoup(res.text, "html5lib")
                data = soup.find(id="airports_in_city_frame")
                locs = data.find(class_="lhs_info").find("ul").find_all("a")
                for loc in locs:
                    if "airports" in loc.text:
                        continue
                    elif "airport" in loc.text:
                        tail_url = loc.get("href")
                        url = head_url + tail_url
                        if url not in url_list:
                            url_list.append(url)
            else:
                tail_url = airport.find("a").get("href")
                url = head_url + tail_url
                if url not in url_list:
                    url_list.append(url)
        except:
            continue
    return url_list


def fetch_data(url):
    locator_domain = "https://www.skyscanner.co.in/"
    location_type = "Airport"
    hours_of_operation = "24 Hrs"
    country_code = "UNITED KINGDOM"
    page_url = url
    url_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.100 Safari/537.36"
    }
    store_number = "<MISSING>"
    location_name = "<MISSING>"
    zip_code = "<MISSING>"
    latitude = "<MISSING>"
    longitude = "<MISSING>"
    street_address = "<MISSING>"
    city = "<MISSING>"
    state = "<MISSING>"
    phone = "<MISSING>"

    sleep(randint(1, 5))
    res = session.get(url, headers=url_headers)
    soup = BeautifulSoup(res.text, "html5lib")
    try:
        location_name = soup.find(id="blurbbox").find("h1").text.replace("\xa0", "")
    except:
        return False
    try:
        coords = soup.find(id="coordbox")
        latitude = coords.find_all("meta")[0].get("content")
        longitude = coords.find_all("meta")[1].get("content")

        geolocator = Nominatim(user_agent="myGeocoder")
        location = geolocator.reverse(latitude + "," + longitude).raw["address"]
    except:
        pass

    try:
        state = location["state"]
    except:
        pass

    try:
        zip_code = location["postcode"]
    except:
        pass

    try:
        street_address = location["road"]
    except:
        pass

    try:
        city = location["city"]
    except:
        pass

    try:
        details = soup.find(id="detailsbox")
        content = details.find(class_="content")
        phone = content.find("td").text
    except:
        pass

    location = []
    location.append(locator_domain)
    location.append(location_name)
    location.append(street_address)
    location.append(city)
    location.append(state)
    location.append(zip_code)
    location.append(country_code)
    location.append(store_number)
    location.append(phone)
    location.append(location_type)
    location.append(latitude)
    location.append(longitude)
    location.append(hours_of_operation)
    location.append(page_url)
    yield location


def scrape():
    work_url = working_url()
    list1 = airports_list(work_url)
    for url in list1:
        data = fetch_data(url)
        if data == False:
            break
        else:
            write_output(data)


scrape()
