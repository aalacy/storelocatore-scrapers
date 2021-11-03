import csv
import re

from bs4 import BeautifulSoup

from sglogging import SgLogSetup

from sgrequests import SgRequests

logger = SgLogSetup().get_logger("pga_com")


def write_output(data):
    with open("data.csv", mode="w") as output_file:
        writer = csv.writer(
            output_file, delimiter=",", quotechar='"', quoting=csv.QUOTE_ALL
        )

        # Header
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
        # Body
        for row in data:
            writer.writerow(row)


def fetch_data():

    user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36"
    headers = {"User-Agent": user_agent}

    session = SgRequests()
    base_url = "https://www.pga.com/play"
    r = session.get(base_url, headers=headers)
    soup = BeautifulSoup(r.text, "lxml")
    addressess = []

    all_state = soup.find("ul", attrs={"data-cy": "states"}).find_all("a")
    for state1 in all_state:
        state_link = "https://www.pga.com" + state1["href"]
        logger.info(state_link)
        try:
            r1 = session.get(state_link, headers=headers)
        except:
            pass

        soup1 = BeautifulSoup(r1.text, "lxml")
        all_city = soup1.find("ul", attrs={"data-cy": "city-list"}).find_all("a")

        for city in all_city:
            city_link = "https://www.pga.com" + city["href"]
            try:
                r2 = session.get(city_link, headers=headers)
            except:
                pass

            soup2 = BeautifulSoup(r2.text, "lxml")
            all_store_link = soup2.find_all(
                "a", {"data-gtm-content-type": re.compile("Facility")}
            )
            for store1 in all_store_link:
                name = ""
                st = ""
                zipp = ""
                tem_var = []
                state = ""
                stopwords = "','"
                new_words = [
                    word
                    for word in list(store1.stripped_strings)
                    if word not in stopwords
                ]

                if len(new_words) == 5:
                    name = new_words[0]
                    state_list = re.findall(
                        r"([A-Z]{2})", str(new_words[-2].strip().lstrip())
                    )
                    if state_list:
                        state = state_list[-1]

                    if len(new_words[1:-2]) == 2:
                        st = new_words[1:-2][0]
                        city = new_words[1:-2][1]

                    us_zip_list = re.findall(
                        re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"), str(new_words[-1])
                    )
                    if us_zip_list:
                        zipp = us_zip_list[-1]

                    page_url = "https://www.pga.com" + store1["href"]

                elif len(new_words) == 4:
                    name = new_words[0]
                    city = new_words[1]
                    us_zip_list = re.findall(
                        re.compile(r"\b[0-9]{5}(?:-[0-9]{4})?\b"),
                        str(new_words[-1].strip().lstrip()),
                    )

                    state_list = re.findall(
                        r"([A-Z]{2})", str(new_words[-2].strip().lstrip())
                    )
                    if state_list:
                        state = state_list[-1]

                    if us_zip_list:
                        zipp = us_zip_list[-1]

                    page_url = "https://www.pga.com" + store1["href"]
                try:
                    r3 = session.get(page_url, headers=headers)
                except:
                    pass

                if "do not use" in st.lower() or "no address available" in st.lower():
                    st = "<MISSING>"
                if not st:
                    st = "<MISSING>"

                soup3 = BeautifulSoup(r3.text, "lxml")
                phone = ""
                try:
                    phone = soup3.find(icon="call").text
                except:
                    pass

                if ", " + state.upper() in st.upper():
                    st = (
                        soup3.find("div", attrs={"data-cy": "course-contacts"})
                        .div.text.split(",")[-1]
                        .strip()
                    )
                    if not st:
                        st = "<MISSING>"

                loc_type = "<MISSING>"
                if "limited to members at this private" in soup3.text.lower():
                    loc_type = "Members Only Private Facility"

                tem_var.append("https://pga.com")
                tem_var.append(name if name else "<MISSING>")
                tem_var.append(st)
                tem_var.append(
                    city.replace("Do not use", "<MISSING>").strip()
                    if city.replace("Do not use", "<MISSING>").strip()
                    else "<MISSING>"
                )
                tem_var.append(state if state else "<MISSING>")
                tem_var.append(zipp if zipp else "<MISSING>")
                tem_var.append("US")
                tem_var.append("<MISSING>")
                tem_var.append(phone if phone else "<MISSING>")
                tem_var.append(loc_type)
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append("<MISSING>")
                tem_var.append(page_url)
                if tem_var[2] in addressess:
                    continue
                addressess.append(tem_var[2])
                yield tem_var


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
