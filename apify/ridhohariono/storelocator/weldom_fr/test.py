from sgzip.dynamic import DynamicGeoSearch, SearchableCountries

search = DynamicGeoSearch(
    country_codes=[SearchableCountries.FRANCE],
    expected_search_radius_miles=600,
    max_search_results=5000,
)
coords = [x for x in search]
coords.append((18.097019874365, -63.042554855347))
for lat, long in coords:
    print(lat, long)
