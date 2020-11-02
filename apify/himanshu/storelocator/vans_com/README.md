### Validation Caveats:
- `--ignore StreetAddressHasNumber` - validator doesn't account for all formats.
- `--ignore StreetAddressHasStateName` - validator doesn't account for all formats.
- `--ignore StateLevelCountValidator` - I'm not sure why that would fail.
- `--ignore GeoConsistencyValidator`  - I suspect this is a data-entry or validator truth-table issue.
- `Validating country-specific information (states, zip codes, phone #'s)` - A few of the addresses are malformed
- ``

address with no number,address contains state name,invalid phon3,zip,same lat & lng