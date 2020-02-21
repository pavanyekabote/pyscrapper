from bs4 import BeautifulSoup

# Get Attribute from object Or Get Index from array etc...
def get_attr_with_err(src_object, index, none_if_empty=False, obj_if_empty=False):
    result, is_error = None, False
    try:
        result = src_object[index]
        if type(result) == list and none_if_empty:
            if len(result) == 0 or len(result) < index:
                result = None
    except:
        is_error = True

    if obj_if_empty:
        if type(result) == list and result == None:
            result = []
        if type(result) == dict and result is None:
            result = {}
    return result, is_error


def get_attr(src_object, index, none_if_empty=False, obj_if_empty=False):
    res, _ = get_attr_with_err(src_object, index, none_if_empty, obj_if_empty)
    return res


def parse_tags(html, structured_tag, eq=None):
    """ Parses structured tags like div .select > #id and fetches its values from html """
    if html is None:
        return []
    # Split with > character
    tag_blocks = structured_tag.split(">")

    for tag_block in tag_blocks:
        selector_tuple = parse_selector(tag_block)
        html = fetch_html_with(*selector_tuple, html, eq=eq)
    return html

def parse_selector(selector):
    """Parses a block of selectors like div .name #tag to class=.name, selector=div and id=#tag.
    Returns (selector, id, class[]) """
    m_class, m_id, m_selector, m_attr = [], None, None, {}
    if selector is not None and type(selector) == str:
        selector_labels = selector.split()
        for label in selector_labels:
            if label.startswith("."):
                m_class.append(label)
            elif label.startswith("#"):
                if m_id is not None:
                    raise ValueError("Multiple id's are declared in block "+str(selector))
                m_id = label
            elif label.startswith("@@"):
                attribute_block = str(label).split('=')
                if len(attribute_block) < 2:
                    raise ValueError('Attribute does not match the \
                    format @@<attribute_name>=<attribute_value> without space')
                attr = attribute_block[0]
                value = attribute_block[1]
                mattr[attr] = value
            else:
                if m_selector is not None:
                    raise ValueError("Multiple selectors are declared in block "+str(selector))
                m_selector = label
    if mattr and not m_selector:
        raise AssertionError('If selection is done with attribute @@<attr_name>=<attr_value>,\
         then it is must to have selector.\n Eg: <selector> @@<attr_name>=<attr_value>"')
    return m_selector, m_id, m_class, mattr


def fetch_html_with(m_selector, m_id, m_class, mattr, html, eq=None):
    if m_id:
        html = listify_soup(html, select=True, tupled_attrs=(m_id), eq=eq)

    elif (m_selector and m_class) or (m_selector and mattr):
        attrs = {}
        if m_class:
            attrs['class'] = ' '.join([cls[1:] for cls in m_class])
        for attr, value in mattr.items():
            attrs[attr] = value

        html = listify_soup(html,tupled_attrs=(m_selector, attrs), eq=eq)

    elif m_selector is None and len(m_class) > 0:
        cls_param = ''.join(m_class)
        html = listify_soup(html, select=True, tupled_attrs=(cls_param,), eq=eq)

    elif m_selector is not None and len(m_class) == 0 and m_id is None:
        html = listify_soup(html, tupled_attrs=(m_selector), eq=eq)
    return html


def listify_soup(soup_object_list, select=False, tupled_attrs = (), eq=None):
    result = []
    is_tuple = type(tupled_attrs) == tuple
    source_arr =  soup_object_list#get_selector_result(soup_object_list, is_select=select, attrs=tupled_attrs)
    if type(soup_object_list) == BeautifulSoup:
        result = [soup for soup in get_selector_result(source_arr, is_select=select, attrs=tupled_attrs, eq=eq)]
    else:
        result = [soup for soup_object in source_arr for soup in \
                  get_selector_result(soup_object, is_select=select, attrs=tupled_attrs, eq=eq) if soup is not None]
    return result


def get_selector_result(soup, is_select=False, attrs = (), eq=None):
    is_tuple = type(attrs) == tuple
    if soup is None:
        return []
    res = []
    if eq is None:
        res = apply_selector(soup,is_select, attrs)
    elif eq is not None and type(eq) == int:
        # Needs some more refactorings, for optimization
        res = [get_attr(apply_selector(BeautifulSoup(str(sub_soup), "html.parser"), is_select, attrs), eq) \
               for sub_soup in soup if str(sub_soup) is not None]
    return res

def apply_selector(soup, is_select=False, attrs=()):
    is_tuple = type(attrs) == tuple
    res = []
    if is_tuple:
        if is_select:
            res = soup.select(*attrs)
        if not is_select:
            res = soup.find_all(*attrs)
    else:
        if is_select:
            res = soup.select(attrs)
        else:
            res = soup.find_all(attrs)
    return res


