import re

"""
Copyright (c) 2015 Andrew Nestico

Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without
restriction, including without limitation the rights to use,
copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following
conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.
"""

def make_replacement_list():
    replacement_list = {}
    with open("Names.txt") as names:
        for line in names:
            parse_line = line.split(":")
            real_name = parse_line[0]
            aliases = parse_line[1].split(",")
            for alias in aliases:
                replacement_list[alias.strip()] = real_name
    return replacement_list

replacement_list = make_replacement_list()


def normalize_name(name):
    """Convert the names in a match to a standarized format: Title case with no sponsors."""

    # Convert all names to titlecase
    name = name.title()

    # Remove pools
    
    name = remove_pools(name)
    """ removing this option for now, creates 0 len string names"""
    """ enable if using BNC """

    """added this to remove emojis lul"""
    name = remove_symbols(name)
    
    # Remove usual sponsors
    name = name.split("|")[-1].strip()
    name = name.split(" I ")[-1].strip()

    # check if name contains an oddly formatted sponsor or otherwise needs to be changed
    for replacement in replacement_list:
        if name == replacement:
            name = replacement_list[replacement]

    return name

def remove_symbols(string):
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags=re.UNICODE)
    string = emoji_pattern.sub(r'', string)
    return string


def remove_pools(string):
    # Things to remove:
    # Anything inside square brackets
    string = re.sub("\[.*\]", "", string).strip()
    # P2/2, (P2-2), etc.
    string = re.sub("\((?:P|)\d+(?:|(?:/:|-)\d+)\)", "", string).strip()
    # A2.2, B2.2, etc.
    string = re.sub("[A-Z]\d+\.\d", "", string).strip()
    # (Wave 2), (Wave2), etc.
    string = re.sub("\(Wave(?: |)\d\)", "", string).strip()
    # (S2 P2), etc.
    string = re.sub("\(S\d+ P\d+\)", "", string).strip()
    # (Setup), (Unpaid), etc.
    string = re.sub("\((?:Setup|Unpaid|Forfeit|Dq|Dnp)\)", "", string).strip()
    return string
