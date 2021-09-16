import argparse
from concurrent import futures
import logging
import os
import yaml

import grpc

import githubsearch
import githubsearch_pb2 as schema
import githubsearch_pb2_grpc

class SearchService(githubsearch_pb2_grpc.GithubSearchService):
    def Search(self, request, context):
        response = schema.SearchResponse()
        response.results.extend(githubsearch.search_code(request.search_term, request.qualifiers))
        return response

def serve(port=50051, max_workers=10):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=max_workers))
    githubsearch_pb2_grpc.add_GithubSearchServiceServicer_to_server(SearchService(), server)
    server.add_insecure_port(f"[::]:{port}")
    logging.info(f"Starting grpc server on port {port}")
    server.start()
    logging.info("Server started")
    server.wait_for_termination()


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", help="Port to serve the application on")
    parser.add_argument("--max-workers", "-w", help="Max number of workers the server should use")
    parser.add_argument("--config", "-c", default=os.environ.get("GITHUB_SEARCH_SERVER_CONFIG", "server-config.yml"), help="Path to yaml config file")
    args = parser.parse_args()

    config = {}

    if os.path.isfile(args.config):
        with open(args.config) as handle:
            config = yaml.safe_load(handle)

    port = args.port if args.port else os.environ.get("GITHUB_SEARCH_SERVICE_PORT", config.get("port", 50051))
    max_workers = args.max_workers if args.max_workers else os.environ.get("GITHUB_SEARCH_MAX_WORKERS", config.get("max_workers", 10))

    serve(port, max_workers)
