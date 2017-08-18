#!/bin/env python

from bs4 import BeautifulSoup


def get_google_links(html):
    """ Uses bs4 to extract links from google """
    # Note, this only works with chromium headers

    soup = BeautifulSoup(html, "html.parser")
    links = []

    # Finds the links
    for div in soup.findAll('h3', {'class': 'r'}):
        a = div.find('a')
        link = a.attrs['href']
        links.append(link)

    # Some links are self-referencing the google search
    # Remove them
    for link in links:
        if link.startswith("/"):
            links.remove(link)

    return links
