Received these errors on validation.

Error 1:

Found 1 rows with inconsistent geographies. Look at the REASON column in the output below to see why these rows were flagged. Examples:
           location_name        street_address    zip  ...   latitude  longitude                REASON
138  Dallas / S. Buckner  2253 S Buckner Blvd.  75527  ...  32.751978  -96.68336  ZIPCODE_NOT_IN_STATE

[1 rows x 8 columns]

Reason: Currently, the site zip code is generated from the site. It seems to be the only value they have inserted incorrectly so it is being ignored until they fix the site.

Error 2:

We think there should be around 214 POI, but your file has 181 POI. Are you sure you scraped correctly?

Reason: I'm using enqueue which adds more sites to the list since I must dig deeper. These are not sites but actually links to help gather more links to find the location link at the end of the road. The restaurant site states there are around 180 locations, so this seems to make sense.
