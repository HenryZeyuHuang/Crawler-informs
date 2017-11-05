import requests
from bs4 import BeautifulSoup
import re


def find_links(all_letters):
    links = []
    for letter in all_letters:
        url = 'https://www.informs.org/Explore/History-of-O.R.-Excellence/Biographical-Profiles/(alpha)/' + letter
        # print(url)
        sourcecode = requests.get(url)
        txt = sourcecode.text
        soup = BeautifulSoup(txt, "html.parser")
        for link in soup.findAll('a'):
            href = link.get('href')
            string = str(href)
            # print(string)
            if len(string) < 54:
                continue
            if string.startswith('/Explore/History-of-O.R.-Excellence/Biographical-Profiles/') and \
                    string[58].isalpha():
                links.append('https://www.informs.org' + href)
    #print(links)
    return links


def find_date(soup):
    name = soup.title.string[0:-10]
    name = name.split(',')
    print(name)
    if len(name) > 2:
        name = [name[0], ','.join(name[1:])]
    for date in soup.findAll('div', {'id': 'lifespan'}):
        # print('So we have to split here')
        # print(date.contents)
        # print(len(date.contents))
        if len(date.contents) == 1:
            if len(date.string) > 5:
                date = str(date.string).strip()
                i_slash = date.index('–')
                if i_slash < 5: born_date = 'N/A'
                else:
                    born_date = date[0:i_slash-9]
                    # i_born = born_date.index(',')
                    # born_date = born_date[0:i_born] + born_date[i_born+1:]
                die_date = date[i_slash+2:]
                # i_die = die_date.index(',')
                # die_date = die_date[0:i_die] + die_date[i_die+1:]
                date = [born_date, die_date]
            else: date = ['N/A', 'N/A']
        else:
            born_date = str(date.contents[2].string).strip()
            # i_born = born_date.index(',')
            # born_date = born_date[0:i_born] + born_date[i_born+1:]
            date = [born_date, 'N/A']
    # print(name + ',' + date)
    return name + date


def if_photos(soup):
    indicator = 'Absent'
    for _ in soup.findAll('img', {'class': 'right dropshadow'}):
        indicator = 'Present'
    # print(indicator)
    return indicator


def bio_word_count(soup):
    brief_bio = ' '
    for string in soup.find('div', {'id': 'bio_header'}).strings:
        brief_bio += string + ' '
    brief_bio = re.sub('[(){}<>]', '', brief_bio)
    word_count = len(brief_bio.replace('\n', ' ').rstrip('?:!.,;()').split())
    # print(word_count)
    return word_count


def wiki_link(soup):
    wiki = 'Absent'
    for link in soup.findAll('a'):
        href = str(link.get('href'))
        if href.startswith('http://en.wikipedia.org/wiki/'):
            wiki = href
    if ',' in wiki:
        wiki = wiki[0:wiki.find(',')]
    # print(wiki)
    return wiki


def contents_after(soup, name, tag_string):
    element = soup.find(name, string = tag_string)
    if element is None: return 'N/A'
    else:
        result = []
        while True:
            element = element.next_sibling
            if element is None: break
            if len(str(element)) < 5:
                continue
            if element.name != 'p': break
            result += [element.text]
    result = ';'.join(result)
    result = " ".join(result.split())
    result = result.replace(',', '')
    result = result.replace(';', '\n')
    # print(result)
    return result


def education(soup):
    return contents_after(soup, 'h3', 'Education')


def other_bio(soup):
    # print(contents_after(soup, 'h5', 'Other Biographies'))
    return contents_after(soup, 'h5', 'Other Biographies')


def awards(soup):
    return contents_after(soup, 'h3', 'Awards and Honors')


def prof_service(soup):
    return contents_after(soup, 'h3', 'Professional Service')


def archives(soup):
    return contents_after(soup, 'h3', 'Archives')


def add_resources(soup):
    return contents_after(soup, 'h3', 'Additional Resources')


def memoirs(soup):
    return contents_after(soup, 'h5', 'Memoirs')


def counts_after(soup, name, tag_string):
    element = soup.find(name, string = tag_string)
    if element is None: return 0
    else:
        result = 0
        while True:
            element = element.next_sibling
            if element is None: break
            if len(str(element)) < 5:
                continue
            if element.name != 'p': break
            result += 1
    return result


def resume(soup):
    return counts_after(soup, 'h5', 'Résumé')


def obituaries(soup):
    return counts_after(soup, 'h3', 'Obituaries')


def publications(soup):
    return counts_after(soup, 'h3', 'Selected Publications')


def h5_match(soup, h5_string):
    lists = soup.find('h5', string = h5_string)
    if lists is None:
        return ['N/A', 'N/A']
    lists = lists.find_next_sibling('ul')
    hist = []
    add = []
    # print(lists.contents)
    lists = [a for a in lists.contents if a != '\n']
    # print(len(lists))
    for element in lists:
        # print(element)
        # print(s for s in element.stripped_strings)
        if len(str(element)) < 5: continue
        if element.find('a') is not None:
            hist += [a for a in element.strings if len(a) > 1]
        else:
            add += [a for a in element.strings if len(a) > 1]
    # print(hist)
    # print(add)
    hist = '\n'.join(hist)
    hist = hist.replace(',', '')
    if hist == '': hist = 'N/A'
    add = '\n'.join(add)
    add = add.replace(',', '')
    if add == '': add = 'N/A'
    return [hist, add]


def academic_ins(soup):
    return h5_match(soup, 'Academic Affiliations')


def non_academic_ins(soup):
    return h5_match(soup, 'Non-Academic Affiliations')


def methodologies(soup):
    return h5_match(soup, 'Methodologies')


def app_areas(soup):
    return h5_match(soup, 'Application Areas')


def pub_no(soup):
    pub = soup.find('h3', text = 'Selected Publications')
    if pub is None:
        return 0
    pub = pub.next_sibling.next_sibling
    count = 0
    while len(str(pub)) > 30:
        #print(str(pub))
        count += 1
        pub = pub.next_sibling
    return count


def oral_hist(soup):
    tag = soup.find('div', {'id': 'oral_hist_block'})
    if tag is None: return ['Absent', 0, 0]
    result = []
    tag_1 = tag.find('h3', string = 'Jump to Chapters')
    if tag_1 is None: result += ['Absent']
    else:  result += ['Present']
    tag_2 = tag.findAll('p')
    num = len(tag_2)
    if result[0] == 'Present': num -= 2
    check = [a.text for a in tag_2]
    num_embedded = sum(['YouTube' in a for a in check])
    result += [num_embedded, num - num_embedded]
    return result


def image(soup):
    tag = soup.find('h3', string = 'Image Gallery')
    if tag is None: return 'Absent'
    else: return 'Present'


def genealogy(soup):
    tag = soup.find('a', string = re.compile('^Mathematics Genealogy'))
    if tag is None: return 'N/A'
    else: return str(tag.get('href'))


def h3_h5(soup):
    tag = soup.findAll('h3')
    tag += soup.findAll('h5')
    result = [a.string for a in tag]
    print(result)
