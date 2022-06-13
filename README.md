# httpbin
A model-based, modern python client implementation for httpbin.org as an example

## Usage
```python
import httpbin


config = httpbin.Config(base_url="https://httpbin.org")
client = httpbin.Client(config)

try:
    get_response = client.get()
except httpbin.ClientError as e:
    print(e)

...
```
