import logging
import requests

import githubsearch_pb2 as schema


def _check_search_validity(search_term, max_len=256, max_operators=5):
    # The github api does not support:
    # - longer than 256 char (not including operators or qualifiers i.e. just the search phrase)
    # - more than five AND, OR, or NOT operators
    # docs: https://docs.github.com/en/rest/reference/search#limitations-on-query-length

    if not search_term:
        raise Exception("search_term required")

    if len(search_term) > max_len:
        raise Exception(f"search_term length is {len(search_term)}. It can not be longer than {max_len}")

    # Case doesn't matter. If you need an and
    # to not act as an operator, then it looks
    # like surrounding the search term in quotes
    # works e.g. prometheus and 'this and that'
    # NOTE: I couldn't find the docs that explicitly
    # said this, but I tested and that's how it's
    # behaving
    wordlist = search_term.lower().split()

    ands = wordlist.count("and")
    ors = wordlist.count("or")
    nots = wordlist.count("not")
    total_operators = ands + ors + nots

    if total_operators > max_operators:
        raise Exception(f"search_term contains too many operators. Max supported is {max_operators}")

def _check_qualifiers(qualifiers):
    for key in qualifiers.keys():
        # NOTE: Case matters on the qualifier keys
        # So not lowercasing the key here is what
        # we want
        if key not in ["user", "org", "repository"]:
            raise Exception(f"Qualifier of type {key} not supported")


def search_code(search_term, qualifiers, per_page=30, page=1, uri="https://api.github.com/search/code"):
    _check_search_validity(search_term)
    _check_qualifiers(qualifiers)

    if per_page > 100:
        raise Exception(f"per_page can not be more than 100 but {per_page} was passed in")

    query = search_term

    for k, v in qualifiers.items():
        query += f" {k}:{v}"

    payload = {"q": query, "per_page": per_page}

    logging.debug(f"Searching github with query: '{query}'")
    response = requests.get(uri, params=payload)

    if response.status_code != 200:
        raise Exception(f"Request did not return 200. status code: {response.status_code} text: {response.text}")

    results = response.json()

    items = []

    for item in response.json().get("items", []):
        result = schema.Result(file_url=item.get("html_url"), repo=item.get("repository", {}).get("html_url"))
        items.append(result)

    # check if pagination has happened.
    # NOTE: left out to avoid rate limits
    # Could pass in number of requests and check that against rate limit
    # if len(items) >= per_page:
    #     items += search(search_term, user, per_page, page+1, uri)

    return items
