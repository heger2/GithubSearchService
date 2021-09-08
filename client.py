import logging
import os

import grpc
import githubsearch_pb2 as schema
import githubsearch_pb2_grpc

SEARCH_SERVICE_URI = os.environ.get("GITHUB_SEARCH_SERVICE_URI", "localhost:50051")

def run():
    with grpc.insecure_channel(SEARCH_SERVICE_URI) as channel:
        stub = githubsearch_pb2_grpc.GithubSearchServiceStub(channel)
        response = stub.Search(schema.SearchRequest(search_term='prometheus', user='microsoft'))

        # NOTE: to call without a user, call search like this. It looks like the API
        # requires you to have a user, org, repo so this will cause an error so I'm
        # not sure how to fulfill all of the requirements
        #response = stub.Search(schema.SearchRequest(search_term='prometheus'))

    if not response.results:
        print("No resulst found")

    for res in response.results:
        print(f"Response: {res}")

if __name__ == '__main__':
    logging.basicConfig()
    run()
