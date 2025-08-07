# bookops-overdrive
An API wrapper for the Overdrive Discovery API.

## Installation
`pip install git+https://github.com/BookOps-CAT/bookops-overdrive.git`

## Basic Usage
```python
with OverdriveSession(authorization=token) as session:
    response = session.get_library_account_info(library_id="1")
    print(response.json())
```
```json
{
    "collectionToken": "",
    "enabledPlatforms": [
        "lightning",
        "libby",
    ],
    "formats": [
        {
            "id": "ebook-mediado",
            "name": "MediaDo eBook",
        },
        {
            "id": "ebook-kindle",
            "name": "Kindle Book",
        },
        {
            "id": "magazine-overdrive",
            "name": "OverDrive Magazine",
        },
        {
            "id": "ebook-overdrive",
            "name": "OverDrive Read",
        },
        {
            "id": "audiobook-overdrive",
            "name": "OverDrive Listen",
        },
    ],
    "id": 837,
    "links": {
        "dlrHomepage": {
            "href": "https://link.overdrive.com?websiteID=",
            "type": "text/html",
        },
        "lists": {
            "href": "https://api.overdrive.com/v1/libraries//lists",
            "type": "application/vnd.overdrive.api+json",
        },
        "products": {
            "href": "https://api.overdrive.com/v1/collections//products",
            "type": "application/vnd.overdrive.api+json",
        },
        "self": {
            "href": "https://api.overdrive.com/v1/libraries/",
            "type": "application/vnd.overdrive.api+json",
        },
    },
    "name": "New York Public Library (NY)",
    "type": "Library",
}
```

## API Documentation
[Client Authentication](https://developer.overdrive.com/api-docs/authentication/client-authentication)
[Discovery APIs](https://developer.overdrive.com/api-docs/discovery-apis)