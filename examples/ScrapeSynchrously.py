from pyscrapper.scrapper import scrape_content, RequestHandler

# Right angular bracket ">" is used,
# to select hierarchal sub elements in html
# Eg : <div class=".header"><h1>Header</h1></div>
# To Select h1 tag value, define .header > h1
# as h1 is subelement/child of .header

# Configuration

CONFIG = {
    "title": ".header > h1",
    "desc": ".header > h2",
    "avatar": {
        "selector": ".header > img",
        "attr": "src"
    }
}
# URL of the webpage to be scrapped
URL = "https://ionicabizau.net"

# Set Max number of parallel request to be performed, if needed.\
# default is count of number of CPU's in system
# Setting MAX_WORKERS to 3, At max only 3 url's can be loaded even in a
# parallel executional enviroment
RequestHandler.MAX_WORKERS = 3

result = scrape_content(URL, CONFIG)
print('Result ',result)

# Output:
# Result
# {
#   'title': 'Ionică Bizău',
#   'desc': 'Programmer,  Pianist,  Jesus follower',
#   'avatar': '/@/bloggify/public/images/logo.png'
#  }
