## PyScrapper
[![PyPI version](https://badge.fury.io/py/pyscrapper@2x.png)](https://badge.fury.io/py/pyscrapper)
[![Downloads](https://pepy.tech/badge/pyscrapper)](https://pepy.tech/project/pyscrapper)
### Introduction
PyScrapper is a web scrapping tool. It helps to scrape webpages and form a meaningful json object, as per the given configuration. Configuration is what tells the scrapper, which blocks of the html needs to be parsed and how they should be structurized for ease of use.	

---
### Installation
 To install from pip
```
pip install pyscrapper
```

---
### Documentation
####  **scrape_content(url, config, to_string=False)**
- import : from pyscrapper.scrapper import scrape_content
- Params : 
	- url : url of webpage to be scraped
	- config : An object containing the scraping information. If you want to scrape a list, you have to use the listItem selector:
		- `listItem (string | object)`: The list item selector.
		- `data (string | object)`: The fields to include in the list objects:
		 -  `<fieldName>(string | object)`: The selector or an object containing:
			 1. `selector (string)`: The selector.
			 2. `attr (string)`: If provided, the value will be taken based on the attribute name.
			 3. `eq (int)`: If provided, it will select the nth element.
			 4. `function(a callable function)`: If provided, it will be called with the current block's data, obtained after parsing the html of current block, on which the user can perform any operation and must return a result... which is then considered as final result of that block.
    - window_size : Specify browser window size in which the url to be loaded
        - default: (1366, 784) # all url's are loaded in 1366, 784 sized browser window by default
#### **MAX_WORKERS :**
 - For thread safety and system load handling... a property named MAX_WORKERS is added...
 - Users are free to decide the number of drivers/browsers can simultaneously be created, while being in a multithreaded environment, just by modifying the MAX_WORKERS property.
 - **For Example :** 
 	- let's say, your system has 8core CPU with 8GB RAM. 
  	- This system can withstand, if tens of drivers/ browsers are parallely running. 
  	- Now, thinking you would like to keep the maximum of 10 drivers/browsers can simultaneously be running on your multithreaded application.
	- In the following way, you can set the maximum drivers limit to 10, as you wished...
```python
from pyscrapper.scrapper import scrape_content
from configurations import url_config_list
from threading import Thread
from pyscrapper.scrapper import RequestHandler

# MAX_WORKERS, is a property of RequestHandler class
# Setting max_workers to 10
RequestHandler.MAX_WORKERS = 10
# The above line makes sure, only 10 drivers at max can be instantiated at once.

# May be there are 100s of urls, configs in url_config_list
# But only 10 urls, configs can be simultaneously executed,
# mean while remaining urls, configs will be in waiting state,
# until any of the executing task is not finished.

# Following code is just to show, that current application is multithreaded
for url, config in url_config_list:
	th = Thread(target=scrape_content, args=(url, config))
	th.start()

```
 ----
 ### Usage : 

In the following example, we are scrapping an URL with the configuration
```python
from pyscrapper.scrapper import scrape_content

# Right angular bracket ">" is used,
# to select hierarchal sub elements in html
# Eg : <div class=".header"><h1>Header</h1></div>
# To Select h1 tag value, define .header > h1 
# as h1 is subelement/child of .header

# Configuration
config = {  
    "title": ".header > h1",  
    "desc": ".header > h2",  
    "avatar": {  
        "selector": ".header > img",  
        "attr": "src"  
  }  
}  
# URL of the webpage to be scrapped
URL = "https://ionicabizau.net"  

# to_string=True allows to return dict converted to json string 
print(scrape_content(URL, config, to_string=True))
```
```javascript
// Output: 
{
  "title": "Ionică Bizău",
  "desc": "Programmer,  Pianist,  Jesus follower",
  "avatar": "/@/bloggify/public/images/logo.png"
}
```
---
**List** Example: 
```python

from pyscrapper.scrapper import scrape_content

config ={  
  "pages": {  
    "listItem": "li .page",  
    "data": {  
      "title": "a",  
      "url": {  
        "selector": "a",  
        "attr": "href"  
  }  
    }  
  }  
}  
  
URL = "https://ionicabizau.net"  
print(scrape_content(URL, config, to_string=True))
```
```javascript
// Output
{
  "pages": [
    {
      "title": "Blog",
      "url": "/"
    },
    {
      "title": "About",
      "url": "/about"
    },
    {
      "title": "FAQ",
      "url": "/faq"
    }
    // ... truncating some part of output, due to space constraint.
  ]
}
```
---

**Function** example:
```python3
from pyscrapper.scrapper import scrape_content

config = {
	"pages": {
    	    "listItem": "li .page",
    	    "data": {
		"title": "a",
		"url": {
		    "selector": "a",
	    	    "attr": "href"
		},
		'title_length' :  { 
	    	    'selector': 'a',
		    # passing a lambda function with one argument, it retuns length of incoming title
	    	    'function': lambda title: len(title) 
	    },
    	}
   }
}
URL = 'https://ionicabizau.net'
print(scrape_content(URL, config, to_string=True))

```
```javascript
// output for above config with function.
{
  "pages": [
    {
      "title": "Blog",
      "url": "/",
      "title_length": 4
    },
    {
      "title": "About",
      "url": "/about",
      "title_length": 5
    },
    {
      "title": "FAQ",
      "url": "/faq",
      "title_length": 3
    }
    // ... truncating some part of output, due to space constraint.
  ]
}
```
Developed with :heart: by  <b>Pavan Kumar Yekabote</b>.
