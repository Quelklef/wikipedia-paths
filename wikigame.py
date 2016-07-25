import re, requests, copy, time

wikipedia_domain = 'http://en.wikipedia.org'

wikipeda_begin_content_flag = '<div id="content"'
wikipeda_end_content_flag = '<div id="mw-navigation"'

def title_to_absolute_link(title):
    """
    Convert a title to a wiki URL
    """
    title = title.replace(' ', '_')
    title = wikipedia_domain + '/wiki/' + title
    return title

class ArticleNotFoundException(Exception):
    pass

def get_html(url):
    req = requests.get(url)
    if req.status_code == 404:
        raise ArticleNotFoundException('No Wikipedia article at {}'.format(url))
    return req.text

def clip_html(html, begin_flag, end_flag):
    """
    Remove the HTML to, but not including, begin_flag;
    remove html after, and including, end_flag,

    i.e. remove everything but that in-between the two flags. Also keep begin_flag.
    """
    content_begin_index = html.index(begin_flag)
    content_end_index = html.index(end_flag)
    return html[content_begin_index:content_end_index]

def extract_html_links(html):
    # Returns a list
    pattern = re.compile('(?<=<a href=["\'])[0-z./]+(?=["\'])')
    return pattern.findall(html)

def remove_extranious_links(links):
    def test_for_needing_removal(link):
        if link[:6] != '/wiki/':
            return True
        link = link[6:]

        disallowed_prefixes = (  # These apply after '/wiki/' is removed
            'File:',
        )

        if link.startswith(disallowed_prefixes):
            return True
        return False

    for link in links:
        if test_for_needing_removal(link):
            links.remove(link)
    return links

def unicode_to_ascii(unicd):
    return unicd.encode('utf-8')

def relative_link_to_title(link):
    """
    /wiki/gold => gold
    /wiki/wood => wood
    /wiki/talk:wood => talk:wood
    """
    return link[6:]

def get_unique_links_on_wiki_page(title):
    try:
        return remove_extranious_links(
#                  list(map(unicode_to_ascii,
                       list(set(  # Remove duplicates
                           extract_html_links(
                               clip_html(
                                   get_html(
                                       title_to_absolute_link(title)
               ), wikipeda_begin_content_flag, wikipeda_end_content_flag)))))#))
    except ArticleNotFoundException:
        return []

class WikiArticle():
    def __init__(self, title, parent=None):
        self.title = title
#        self.children = []
#        self.gave_birth = False
        self.parent = parent

    @property
    def link(self):
        return title_to_absolute_link(self.title)

    @property
    def links(self):
        return get_unique_links_on_wiki_page(self.title)

    def give_birth(self, forbidden_titles=[]):
        """
        Create a new WikiArticle object for each link on this page #and add said objects to a list and to `.children`
        """
        new_article_titles = set()
        new_articles = set()
        for link in self.links:
            link_as_title = relative_link_to_title(link)
            if not link_as_title in forbidden_titles:
                child = WikiArticle(link_as_title, parent=self)
#                self.children.append(child)
                new_articles |= {child}
                new_article_titles |= {link_as_title}
#        self.gave_birth = True
        return new_articles, new_article_titles


def find_shortest_path_between_two_articles(article_1_title, article_2_title):
    links = get_unique_links_on_wiki_page(article_1_title)
    titles = list(map(relative_link_to_title, links))
    articles = set(map(WikiArticle, titles))

    finished_articles = set()
    todo_articles = set()

    todo_articles |= articles

    visited_articles_titles = set()  # A set of titles of articles we've already visited.
    # We'll use this to make sure that we do not visit a page we are already testing

    the_article_of_destiny = None
    destination_article_found = False
    while not destination_article_found:

        for a in todo_articles:
            if a.title.lower() == article_2_title.lower():
                the_article_of_destiny = a
                destination_article_found = True
                break

        if not destination_article_found:  # Keep this after article testing
            new_articles = set()
            for a in todo_articles:
                articles_birthed, birthed_article_titles = a.give_birth(forbidden_titles=visited_articles_titles)
                new_articles |= articles_birthed
                visited_articles_titles |= birthed_article_titles
            finished_articles |= todo_articles
            todo_articles = new_articles

    # Return final path
    path = []
    article = the_article_of_destiny
    while article.parent is not None:
        path.append(article.title)
        article = article.parent
    path.append(article.title)  # Root article
    path.append(article_1_title)

    path.reverse()

    return ' => '.join(path)

def time_time_prettify(seconds):
    units = [
        ('ms', None),
        ('s', 1000),
        ('m', 60),
        ('h', 60),
        ('d', 24),
    ]

    separated = []

    ms = seconds * 1000
    value = ms
#    print(value)
    for unit in units[1:]:
        leftover = value % unit[1]
        value //= unit[1]

        separated.append(leftover)
#        print(separated)
    # last unit
    separated.append(value)
#    print(separated)

    final = []
    for value_index in range(len(separated)):
        value = separated[value_index]
        if value != 0:
            if int(value) == value:
                value = int(value)  # Remove excess 0s
            string = str(value)
            string += units[value_index][0]
            final.append(string)

    final.reverse()
    return ', '.join(final)

if __name__ == '__main__':
    source_title = raw_input('Source title: ')
    destination_title = raw_input('Dest title: ')

    try:
        start_time = time.time()
        start_clock_time = time.clock()

        print(find_shortest_path_between_two_articles(source_title, destination_title))

        end_time = time.time()
        end_clock_time = time.clock()

        time_elapsed = end_time - start_time
        clock_time_elapsed = end_clock_time - start_clock_time

        print('Time elapsed:\n{}'.format(time_time_prettify(time_elapsed)))
        print('Clock time elapsed:\n{}'.format(time_time_prettify(clock_time_elapsed)))
    except ArticleNotFoundException as e:
        print(e)
