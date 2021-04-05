import csv
import time
from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs
from sgselenium import SgSelenium
import re

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


def fetch_data():
    headers = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.96 Safari/537.36",
    }
    soup = bs(
        session.get(
            "https://www.worldmarkbywyndham.com/resorts/index.html", headers=headers
        ).text,
        "html5lib",
    )
    child_selection = soup.find(
        lambda tag: (tag.name == "script")
        and "let's populate all child values in array" in tag.text
    ).text.split("value:")[1:]
    for value in child_selection:
        page_url = (
            "https://www.worldmarktheclub.com/resorts/"
            + str(value.split('"')[1].replace(".", "").replace("/", ""))
            + "/"
        )
        user_agent = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36"
        driver = SgSelenium().firefox(user_agent=user_agent)
        driver.get(page_url)
        time.sleep(5)
        soup = bs(driver.page_source, "html5lib")
        RightFeature = len(soup.find_all("td", {"class": "RightFeature"}))
        if RightFeature == 2:
            data = list(
                bs(
                    str(soup.find_all("td", {"class": "RightFeature"})[1]).split(
                        "Credit Values"
                    )[0],
                    "html5lib",
                ).stripped_strings
            )
        else:
            data = list(
                bs(
                    str(soup.find_all("td", {"class": "RightFeature"})[2]).split(
                        "Credit Values"
                    )[0],
                    "html5lib",
                ).stripped_strings
            )
        coords = soup.find("a", text=re.compile("Resort Directions"))
        if coords:
            coords = coords["href"]
            lat = coords.split("lat=")[1].split("&")[0]
            lng = coords.split("long=")[1].split("&")[0]
        else:
            lat = "<MISSING>"
            lng = "<MISSING>"
        try:
            location_name = soup.find("div", {"class": "title"}).text.strip()
        except:
            location_name = soup.find("span", {"class": "title"}).text.strip()
        if (
            "Mexico" in " ".join(data)
            or "Fiji" in " ".join(data)
            or "Australia" in " ".join(data)
        ):
            continue
        for index, value in enumerate(data):
            if (
                value.replace("-", "").lower().strip() == "email"
                or "(When " in value
                or "Unit Types" in value
                or "PLEASE NOTE" in value
            ):
                del data[index:]
                break
        try:
            if "WorldMark" in data[0]:
                del data[0]
            if not re.findall(r"[0-9]+", data[0]):
                del data[0]
            if not re.findall(r"[0-9]+", data[0]):
                del data[0]
            if "Fax" in data[-1] or "F:" in data[-1]:
                del data[-1]
            if (
                data[-1]
                .replace("-", "")
                .replace("Ph", "")
                .replace("(", "")
                .replace(")", "")
                .replace("P:", "")
                .replace(" ", "")
                .strip()
                .isdigit()
            ):

                phone = data[-1].replace("Ph", "").replace("P:", "").strip()
                del data[-1]
            else:
                phone = "<MISSING>"
            if data[-1] == "Canada":
                del data[-1]
            street_address = data[0]
            if "\n" in data[0]:
                street_address = data[0].split("\n")[0]
                city = data[0].split("\n")[1].split(",")[0]
                state = data[0].split("\n")[1].split(",")[1].split()[0]
                zipp = data[0].split("\n")[1].split(",")[1].split()[1]
            else:
                del data[0]
                if len(data) == 1:
                    if "," not in data[0]:
                        city = data[0].split()[0]
                        state = data[0].split()[1]
                        zipp = data[0].split()[2]
                    else:
                        city = " ".join(data[0].split(",")[:-1])
                        partial_info = data[0].split(",")[-1].split()
                        if len(partial_info) == 2:
                            state = partial_info[0].replace("V8E", "<MISSING>")
                            zipp = partial_info[1].replace("0M8", "V8E 0M8")
                        elif len(partial_info) == 3:
                            state = partial_info[0]
                            zipp = " ".join(partial_info[1:])
                        else:
                            state = " ".join(partial_info[:-1])
                            zipp = partial_info[-1]
                else:
                    if data[0] == "Drive":
                        street_address += " " + data[0]
                        city = data[1].split(",")[0]
                        state = data[1].split(",")[1].split()[0]
                        zipp = data[1].split(",")[1].split()[1]
                    else:
                        city = data[0].split(",")[0]
                        state = data[0].split(",")[1].strip()
                        zipp = data[-1]
                store = []
                store.append("https://www.worldmarkbywyndham.com/")
                store.append(location_name)
                store.append(street_address)
                store.append(city)
                store.append(state)
                store.append(zipp)
                store.append("US" if zipp.replace("-", "").strip().isdigit() else "CA")
                store.append("<MISSING>")
                store.append(phone)
                store.append("RESORT")
                store.append(lat)
                store.append(lng)
                store.append("<MISSING>")
                store.append(page_url)
                store = [
                    x.replace("–", "-") if isinstance(x, str) else x for x in store
                ]
                store = [x.strip() if isinstance(x, str) else x for x in store]
                yield store
                driver.quit()
        except:
            continue


def scrape():
    data = fetch_data()
    write_output(data)


scrape()
