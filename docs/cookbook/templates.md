# Cookbook - Templates
* The crawler templates are located in `./templates`.
* The selected template folder contents are meant to be copied over to the implementation directory.
    * See the [directory skeleton](dir_skeleton.md) listing.

## Legacy Node.js Templates
* Located in `./templates/node_js`
* Maintained to offer the option of implementing a Node.js crawler (not recommended).

## Python3 Templates
* Located in `./templates/python`
* They make use of the `sgcrawler` engine, and offer two functionally-equivalent flavours:
    * The __Succinct__ form makes use of passing functions, and is more readable/succinct.
        * Located in `./templates/python/succinct`
    * The __Object Oriented__ form makes of class inheritence, and is more familiar to some.
        * Located in `./templates/python/object_oriented`
* Each flavour has several templates based on the capabilities they offer:
    * `basic` - offers the bare-bones engine.
    * `with_http_client` - offers the engine with a simple or headless-browser http client.
    * `with_http_client_and_dynamic_search` - engine with http client, and dynamic zip/coord search.
    * `with_http_client_and_static_coordinate_list` - - engine with http client, and static coordinate list.
    * `with_http_client_and_static_zipcode_list` - - engine with http client, and static zipcode list.