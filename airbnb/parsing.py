from dataclasses import dataclass
from bs4 import BeautifulSoup
from typing import Dict, Set

"""
This files contain the functions that parse the 
nodes of DOM we are interested in. They are not 
stable and would need to be tweaked as often as
the DOM on the called end changes and are also
specific for this particular scraping.

There is a representation of the expected result 
of the scraping with a dataclass object. 

Here I am assuming that only valid resources will be returned
and that all defined attributes will have values.

"""


@dataclass
class AbnbResult:
    external_id: int
    guests: int
    bedroom: int
    bed: int
    bathroom: int
    amenities: list


def parse_overview_line(resource_id: int, line: str) -> Dict[str, int]:
    overview_split = line.split("·  ·")

    overview_data = {}
    for item in overview_split:
        value, name = item.strip().split(" ")
        overview_data[name] = int(value)

    return overview_data


def parse_amenities_list(page_content: str) -> Set[str]:
    """
    I did not find any reliable ids I could attach to and I am new to
    Playwright. Pressed by time, I used BeautifulSoup to navigate the
    DOM and parse the amenties list on the page.

    The parsing of the amenities is minimal.
    Depending on the use of this information it may make sense to
    provide more structured amenities information.
    """

    soup = BeautifulSoup(page_content, "html.parser")
    parsed_amenities = soup.find_all(attrs={"aria-label": "What this place offers"})

    amenities_set = set()

    for item in parsed_amenities[0].descendants:

        if item.string is not None:
            amenities_set.add(item.string)

    return amenities_set
