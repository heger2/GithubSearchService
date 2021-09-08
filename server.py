from concurrent import futures
import logging
import os

import grpc

import githubsearch_pb2 as schema
import githubsearch_pb2_grpc

import utils

SERVER_PORT = os.environ.get("GITHUB_SEARCH_SERVICE_PORT", "50051")

class SearchService(githubsearch_pb2_grpc.GithubSearchService):
    def Search(self, request, context):
        response = schema.SearchResponse()
        response.results.extend(utils.search_code(request.search_term, request.user))
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    githubsearch_pb2_grpc.add_GithubSearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port(f"[::]:{SERVER_PORT}")
    print(f"Starting grpc server on port {SERVER_PORT}")
    server.start()
    print("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig()
    serve()
