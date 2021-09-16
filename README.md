# GithubSearchService

To run first install the requirements
```
pip install -r requirements.txt
```

## Passing arguments
Both the client and the server can be passed args to modify their default behavior. They can take in args from the cli, from env vars, or from a yaml config file. The order of precedence is cli arg > env var > config file.

## Server
Run the server by executing the server.py script
```
python server.py
```
Overrides can be seen in the help. The help can be seen by adding the --help flag e.g.
```
❯ python server.py --help
usage: server.py [-h] [--port PORT] [--max-workers MAX_WORKERS]

optional arguments:
  -h, --help            show this help message and exit
  --port PORT, -p PORT
  --max-workers MAX_WORKERS, -w MAX_WORKERS
```
env vars:
```
GITHUB_SEARCH_SERVER_CONFIG=path/to/config.yml
GITHUB_SEARCH_PORT=50051
GITHUB_SEARCH_MAX_WORKERS=10
```
config file:
```
port: 50051
max_workers: 10
```

## Client
To test that it's working, you can run the client while the server is running e.g. the following query will search the microsoft user's repositories for files containing prometheus in them:
```
python client.py -s prometheus -q user=microsoft
```
You can see the client help by adding the --help flag e.g.
```
❯ python client.py --help
usage: client.py [-h] --search_term SEARCH_TERM --qualifier QUALIFIER [--service-uri SERVICE_URI]

optional arguments:
  -h, --help            show this help message and exit
  --search_term SEARCH_TERM, -s SEARCH_TERM
                        Search term to search for
  --qualifier QUALIFIER, -q QUALIFIER
                        Qualifier to add to the search. Format should be <qualifier>=<value> e.g. user=microsoft
  --service-uri SERVICE_URI, -u SERVICE_URI
                        URI for the

```
env vars:
```
GITHUB_SEARCH_CLIENT_CONFIG=path/to/config.yml
GITHUB_SEARCH_SEARCH_TERM="some search term"
GITHUB_SEARCH_QUALIFIERS=user:foo,org:bar
GITHUB_SEARCH_SERVICE_URI=localhost:50051
```
config file:
```
search_term: some search term
service_uri: localhost:50051
qualifiers:
  user: foo
  org: bar
```
