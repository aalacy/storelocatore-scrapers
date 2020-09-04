import csv
from sgselenium import SgSelenium
import re
from bs4 import BeautifulSoup

driver = SgSelenium().chrome()


def write_output(data):
    with open('data.csv', mode='w') as output_file:
        writer = csv.writer(output_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)

        # Header
        writer.writerow(["locator_domain", "location_name", "street_address", "city", "state", "zip", "country_code",
                         "store_number", "phone", "location_type", "latitude", "longitude", "hours_of_operation",
                         "page_url"])
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():
    # Your scraper here
    locs = []
    street = []
    states = []
    cities = []
    types = []
    phones = []
    zips = []
    long = []
    lat = []
    timing = []
    ids = []
    page_url = []

    driver.get("https://studiobarre.com/find-your-studio/")
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    statel = soup.find_all('div', {'style': 'padding-top:50px; padding-bottom:0px; background-color:'})

    for sl in statel:
        h5s = sl.find_all("h5")
        ps = sl.find_all('p', {'class', 'big'})
        for p in ps:
            addr = p.text.replace("View on Map", "").strip()
            addr = addr.split(",")
            z = re.findall(r'[0-9]{5}', addr[-1].strip())
            if z == []:
                zips.append("<MISSING>")
                states.append(addr[-1])

            else:
                zips.append(z[0])
                states.append(addr[-1].replace(z[0], ""))
            del addr[-1]
            if "Great Falls" in addr[-1]:
                cities.append("Great Falls")
            else:
                cities.append(addr[-1])
                del addr[-1]
            st = ""
            for ad in addr:
                st += ad

            street.append(st.replace("Great Falls", ""))
        for h in h5s:
            a = h.find_all("a")
            if a != []:
                locs.append(a[0].text)
                page_url.append(a[0].get('href'))
            else:
                locs.append(h.text)
                page_url.append("https://" + h.text.strip().lower() + ".studiobarre.com/")

    for url in page_url:
        print(url)

        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')

        spans = soup.find_all('span', {'class': 'elementor-icon-list-text'})
        phones.append(re.sub(r'[\{\}a-z ]*', "", spans[1].text.strip()))
        print(re.sub(r'[\{\}a-z ]*', "", spans[1].text.strip()))

        try:
            div = driver.find_element_by_xpath("/html/body/div[1]/div[1]/div/div/div/section[4]")
        except:
            try:
                div = driver.find_element_by_xpath("/html/body/div[1]/div[2]/div/div/div/section[4]")
            except:
                timing.append('<MISSING>')
                continue
        divas = div.find_elements_by_class_name("elementor-widget-container")
        del divas[0]
        del divas[0]
        tim = ""

        for div in divas:

            try:
                h3s = div.find_element_by_tag_name('h3')
            except:
                break
            dvs = div.find_elements_by_class_name('desc')

            tim += h3s.text
            for ds in dvs:
                tim += " " + ds.text + " "

            if dvs == []:
                s = str(soup)
                divs = re.findall(r'<!--div class="desc">(.*)</div-->', s)
                tim += " " + divs[divas.index(div)] + " "

            tim = tim.replace("\n", " ")
        if tim == "":
            tim = "<MISSING>"
        timing.append(tim.strip())

    all = []
    for i in range(0, len(locs)):
        row = []
        row.append("https://studiobarre.com")
        row.append(locs[i])
        row.append(street[i])
        row.append(cities[i])
        row.append(states[i])
        row.append(zips[i])
        row.append("US")
        row.append("<MISSING>")  # store #
        row.append(phones[i])  # phone
        row.append("<MISSING>")  # type
        row.append("<MISSING>")  # lat
        row.append("<MISSING>")  # long
        row.append(timing[i])  # timing
        row.append(page_url[i])  # page url

        all.append(row)
    return all


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
