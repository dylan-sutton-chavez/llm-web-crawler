import requests as r
from url_normalize import url_normalize
from lxml import html
from html_to_markdown import convert_to_markdown
import jsonlines

from xai_sdk import Client
from xai_sdk.chat import user, system

from os import getenv
from time import perf_counter

class Crawler:
    def __init__(self, root: str):
        """
        initialize the `session`, `queue`, `visited`, `xai_client`, and `system-prompt`

        args:
            root: str → define the seed url
            
        return:
            None
            
        time complexity → o(1)
        """
        self.session = r.Session()

        self.queue: set = {root}
        self.visited = set()
        
        self.xai_client = Client(api_key=getenv('XAI_API_KEY')) # load the xai api key enviroment variable

        # open the system prompt and store in cache
        with open("system-prompt.md", 'r', encoding="UTF-8") as f:
            self.system_prompt = f.read()

    def node(self, filename=str, depth=int):
        """
        create a node that manage the crawling loop process

        args:
            filename: str → name of the file that stores the crawled content
            depth: int → define the depth of the crawl

        return:
            None

        time complexity → o(d*T(_get_queue))
        """
        for current_depth in range(depth):
            finded_urls, elapsed_time = self._get_queue(filename)

            print(f'Depth {current_depth + 1}/{depth}:\n    {len(self.queue)} Sites Crawled | {str(elapsed_time)[:9]} Seconds\n')

            # update the visited sites and update the queue
            self.visited.update(self.queue)
            self.queue = finded_urls - self.visited

    def _get_queue(self, filename: str):
        """
        loop that process each url in the queue
        
        args:
            filename: str → name of the file that stores the crawled content

        return:
            finded_urls: set → site urls
            float → total time of the loop

        time complexity → o(n*T(process site))
        """
        start = perf_counter()

        finded_urls = set()

        # itereate for each url in the queue cache
        for url in self.queue:
            content = self._parse_website(url)

            # check if exists a requests or format error
            if isinstance(content, dict):
                print(content['error'])
                continue

            site_obj = {
                "reference": url,
                "content": self._sanitize_markdown(convert_to_markdown(content))
            }

            self._append_json(site_obj, filename)
            
            tree = html.fromstring(content) # create an HTML tree object

            finded_urls.update(self._find_urls(tree, url))

        return finded_urls, perf_counter() - start

    def _parse_website(self, url: str):
        """
        with the current session parse a website and extracte the html

        args:
            url: str → url to parse
        
        return:
            str → full html content
            dict → raise an error in a dict

        time complexity → o(1)
        """
        try:
            response = self.session.get(url, timeout=7) # get the site content

            # check http response
            if response.status_code != 200:
                return {"error": f"Error HTTP {url}: {response.status_code}"}
            
            content_type = response.headers.get('Content-Type', '').lower()

            # verify if the content its a HTML file
            if 'text/html' not in content_type:
                return {"error": f"Not HTML {url}: {content_type[:32]}"}
            
            return response.text
        
        # handle the requests exceptions
        except r.exceptions.RequestException as e:
            return {"error": f"Request exception {url}: {str(e)[:32]}"}
        
        # raise all the other exceptions of the request
        except Exception as e:
            return {"error": f"An esception ocurred {url}: {str(e)[:32]}"}
    
    def _find_urls(self, tree, root: str):
        """
        search all the urls and return in a set

        args:
            tree: HtmlElement → tree of html elements
            
        return:
            urls: set → sanitized urls

        time complexity → o(L)
        """
        urls = set()

        # create a loop for each url label
        for url in tree.xpath('//a/@href'):

            # add the normal urls to the set
            if url.startswith('https://'):
                urls.add(url_normalize(url, filter_params=True))

            # complete and save the relative urls
            elif url.startswith('/'):
                urls.add(url_normalize(root + url, filter_params=True))

        return urls
    
    def _append_json(self, obj: dict, filename: str):
        """
        append linea-per-line into the file

        args:
            obj: dict → reference (url site), and content in markdown format 
            filename: str → name of the json file
        
        return:
            None

        time complexity → o(1)
        """
        with jsonlines.open(filename, mode='a') as writer:
            writer.write(obj)

    def _sanitize_markdown(self, raw_md: str):
        """
        use a llm to sanitize the markdown content

        args:
            raw_md: str → raw markdown
        
        return:
            str → sanitized markdown

        time complexity → o(1)
        """
        chat = self.xai_client.chat.create(model='grok-4-fast-non-reasoning')
        chat.append(system(self.system_prompt))
        chat.append(user(raw_md))

        response = chat.sample()
        
        return response.content

if __name__ == '__main__':
    """execute this block only when the script is run directly"""

    # import and load enviroment variables (xai_sdk)
    from dotenv import load_dotenv
    load_dotenv()

    # initialize the crawler wirh a seed url
    constructor = Crawler('https://www.geeksforgeeks.org/machine-learning/what-is-perceptron-the-simplest-artificial-neural-network/')
    
    # start a node in the crawler object with a depth of two

    constructor.node(filename='crawled-sites.jsonl', depth=2)
