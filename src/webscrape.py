import requests
from bs4 import BeautifulSoup

headers = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}

def translate(verb):
    to_remove = ["etwas", "sich", "jemand", "jemanden", "jemandem", "jemanden/etwas", "viel/wenig/nichts", "sich/jemanden", "es", "sich/jemanden/etwas", "sich/jemandem/etwas", "(sich)", "..."]

    for t in to_remove:
        verb = verb.replace(t, "")

    url = "https://www.verbformen.com/?w=" + verb

    s = requests.Session()
    r = s.get(url, headers=headers)

    soup = BeautifulSoup(r.content, "html.parser")

    tr = soup.find("span", lang="en")

    if tr == None:
        return "Ubersetzung nicht verfugbar"

    translation = tr.text

    v = 0
    for i in range(len(translation)):
        if translation[i] == ",":
            v += 1

        if v >= 3 or i == len(translation) - 1:
            v = i
            break

    return translation[2:v]
