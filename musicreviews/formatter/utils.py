"""
Helpers for review and index formatting.
- Parsers format and combine lists of dictionaries using formatters.
"""


def parse_list(data, formatter, index_shift=1):
    """Parses each element in data using a formatter function.
    Data is a list of dicts.
    """
    output = ''.join([formatter(i + index_shift, item) for i, item in enumerate(data)])
    return output


def parse_categorised_lists(
    data,
    header_formatter,
    formatter,
    index_shift=1,
    sorted_keys=None
):
    """Parses each element in data using a formatter function.
    Data is a dict, each key is a category and each value is a list of dicts.
    Adds a header for each category.
    """
    if sorted_keys is None:
        sorted_keys = sorted(data.keys(), reverse=True)
    output = ''.join(
        [
            header_formatter(key) + parse_list(data[key], formatter, index_shift)
            for key in sorted_keys
        ]
    )
    return output
