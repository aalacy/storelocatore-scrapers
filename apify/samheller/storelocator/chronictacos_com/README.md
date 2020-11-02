
## Ignore StateLevelCountValidator

State Count 
```
When we looked at the number of POI in your data by state, we noticed large differences for 1 states in total. This might be because you incorrectly scraped data for these states (though it might also indicate an issue with our truthset or with differences in how we format states. Below are a handful of state for which we noticed issues. Go back to the store locator to ensure you're scraping the correct number of locations. If you think that this is a problem with our truthset or validation code, ignore this check and write down your reasoning for skipping the check in your README.

Example of states in your data that overlap with our truthset but which have significant differences in counts:
   expected_cnt  your_cnt state
0           8.0        29    CA
```
29 is accurate count, see `chronictaco_ca_locations.png` for screenshot.

Unexpected States
```
Examples of states that we saw in your data but didn't expect to see: ['AZ' 'TX'].
```
Arizona and Texas both have store locations see `chronictacos_az_locations.png` and `chronictacos_tx_locations.png` for screenshots.