import argparse
import logging
import os
import yaml

import grpc
import githubsearch_pb2 as schema
import githubsearch_pb2_grpc

def run(uri, search_term, qualifiers):
    with grpc.insecure_channel(uri) as channel:
        stub = githubsearch_pb2_grpc.GithubSearchServiceStub(channel)
        response = stub.Search(schema.SearchRequest(search_term=search_term, qualifiers=qualifiers))

    if not response.results:
        logging.info("No results found")

    for res in response.results:
        logging.info(f"Response: {res}")

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser()
    parser.add_argument("--search-term", "-s", help="Search term to search for")

    # NOTE: The append action allows you to pass this flag in multiple times
    # And it will show up as a list
    parser.add_argument("--qualifier", "-q", action='append', help="Qualifier to add to the search. Format should be <qualifier>:<value> e.g. user=microsoft")
    parser.add_argument("--service-uri", "-u", help="URI for the githubsearch service")
    parser.add_argument("--config", "-c", default=os.environ.get("GITHUB_SEARCH_CLIENT_CONFIG", "client-config.yml"), help="Path to yaml config file")
    args = parser.parse_args()

    config = {}

    if os.path.isfile(args.config):
        with open(args.config) as handle:
            config = yaml.safe_load(handle)

    search_term = args.search_term if args.search_term else os.environ.get("GITHUB_SEARCH_SEARCH_TERM", config.get("search_term"))
    service_uri = args.service_uri if args.service_uri else os.environ.get("GITHUB_SEARCH_SERVICE_URI", config.get("service_uri", "localhost:50051"))
    qualifiers = args.qualifier if args.qualifier else os.environ.get("GITHUB_SEARCH_QUALIFIERS", "").split(",")

    # NOTE: not trying to grab qualifiers from config here since the config will have a different format
    # and I'm cleaning up the array in case the environment variable is empty. That'll return an array
    # with one item that's an empty string the way it's set up right now
    qualifiers = list(filter(None, qualifiers))


    qualifiers_formatted = {}

    if qualifiers:
        for qualifier in qualifiers:
            if not qualifier:
                continue

            if ":" not in qualifier:
                logging.error(f"Invalid qualifier format. Format should be <qualifier>:<value> e.g. user=microsoft. Got '{qualifier}'")
                exit(1)

            k, v = qualifier.split(":")
            qualifiers_formatted[k] = v
    else:
        qualifiers_formatted = config.get("qualifiers")

    if not search_term:
        logging.error("Search term is required")
        exit(0)

    if not qualifiers_formatted:
        logging.error("At least one qualifier is required")
        exit(0)

    run(service_uri, search_term, qualifiers_formatted)
