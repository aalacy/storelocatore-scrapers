from sgrequests import SgRequests
from bs4 import BeautifulSoup as bs

session = SgRequests()

response = session.get("https://legacy.webster.edu/locations/index.xml").text
soup = bs(response, "html.parser")

placemarks = soup.find_all("placemark")
for placemark in placemarks:
    placemark = placemark.text

    placemark = place

