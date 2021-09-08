import requests
import githubsearch_pb2 as schema

SEARCH_TERM_MAX_LEN = 256
SEARCH_TERM_MAX_OPERATORS = 5

def _check_search_validity(search_term):
    # The github api does not support:
    # - longer than 256 char (not including operators or qualifiers i.e. just the search phrase)
    # - more than five AND, OR, or NOT operators
    if not search_term:
        raise Exception("search_term required")

    if len(search_term) > SEARCH_TERM_MAX_LEN:
        raise Exception(f"search_term length is {len(search_term)}. It can not be longer than {SEARCH_TERM_MAX_LEN}")

    wordlist = search_term.lower().split()

    ands = wordlist.count("and")
    ors = wordlist.count("or")
    nots = wordlist.count("not")
    total_operators = ands + ors + nots

    if total_operators > 5:
        raise Exception(f"search_term contains too many operators. Max supported is {SEARCH_TERM_MAX_OPERATORS}")


def search_code(search_term, user=None, per_page=30, page=1, uri="https://api.github.com/search/code"):
    _check_search_validity(search_term)

    if per_page > 100:
        raise Exception(f"per_page can not be more than 100 but {per_page} was passed in")

    # NOTE: it looks like the api requires a user
    # org or repository, so we should probably require
    # that a user is passed in or at least some other
    # qualifier https://docs.github.com/en/github/searching-for-information-on-github/searching-on-github/searching-code#considerations-for-code-search
    query = search_term + (f" user:{user}" if user else "")
    payload = {"q": query, "per_page": per_page}

    response = requests.get(uri, params=payload)

    if response.status_code != 200:
        raise Exception(f"Request did not return 200. status code: {response.status_code} text: {response.text}")

    results = response.json()

    items = [schema.Result(file_url=x.get("html_url"), repo=x.get("repository", {}).get("html_url")) for x in response.json().get("items", [])]

    # check if pagination has happened.
    # NOTE: left out to avoid rate limits
    # Could pass in number of requests and check that against rate limit
    #if len(items) >= per_page:
    #    items += search(search_term, user, per_page, page+1, uri)

    return items
