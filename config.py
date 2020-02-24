url = 'https://www.msn.com/en-in/health/health-news'
list_config = {
            'listItem': ".rc-item-js",
            'data': {
                'content_link': {
                     'selector': 'a .contentlink',
                     'attr': 'href'
                },
            }
}
base_url = 'https://www.msn.com'
next_config = {
            'image': {
                'selector': 'section .articlebody > span .storyimage > img .loaded',
                'attr': 'src'
            },
            'title': 'header .collection-headline-flex > h1',
            'body': {
                'selector': 'section .flexarticle > p',
                'function': lambda p: len(p)
            }
}
