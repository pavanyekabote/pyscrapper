.. _scrape-reflabel:

##############
Configuration
##############

Configuration is the most important part of PyScrapper.
This is the only way, by which you can tell the parser, what you actually want from the scrapped html web page.

Basics of defining, configuration
----------------------------------

* Configuration is expected to be as python dict, containing the keys as user defined names and values to be the html selectors.
* There are some predefined keys, which must only be used to define the structure of configuration

    * :file:`listItem (string | object)`:The list item selector.
    * :file:`data (string | object)`:The fields to include in the list objects
    * :file:`<fieldName> (string | object)`: The selector or an object containing:

        * :file:`selector (string)`: The selector ( html id or class selector).
        * :file:`attr (string)`: If provided, the value is taken from the markup's attribute name.
        * :file:`eq (int)`: If provided, it will select the nth element.
        * :file:`function(a callable function)`: If provided, it will be called with the current block's data, obtained after parsing the html of current block, on which the user can perform any operation and must return a result... which is then considered as final result of that block.

