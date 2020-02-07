from bs4 import BeautifulSoup as bs
from urllib.request import urlopen
from dateutil.parser import parse
import re

def main():
    url = "https://www.imdb.com/search/title/?companies=co0041930&sort=release_date,desc&view=simple"
    page = urlopen(url)
    soup = bs(page, 'html.parser')  
    page_count = 0
    # Process the page by recursively following hyperlinks
    # List of items/films from the page
    while(page_count <= 500):
        for l in soup.find_all('div', attrs={'class':'lister-item mode-simple'}):
            # Count variable for page start
            page_count = page_count + 1
            # Scan through the elements of each item from the list
            itm = l.find('div', {'class':'lister-item-content'})
            col = itm.find('div', {'class':'col-title'})
            x = col.find('span', {'class':'lister-item-header'})
            link = x.find('a')
            #Film name
            film_name = link.text
            next_url = "https://www.imdb.com" + link['href']
            tech_specs_url = "https://www.imdb.com" + link['href'] + "technical"
            
            title = bs(urlopen(next_url), 'html.parser')
            t_bar = title.find('div', {'class':'titleBar'})
            sub_text = t_bar.find('div', {'class':'subtext'})
            values = sub_text.text.strip().split('|')

            # Release date
            release_date = ""
            tv_series = False
            temp_date = values[-1].replace('\n', '').strip()
            try:
                if "TV Series" in temp_date:
                    tv_series = True
                    # Dash used for split is unicode: '\u2014'
                    years = re.search('\((.*)\)', temp_date)[1].split('–')
                    if is_date(years[0]):
                        release_date = str(years[0])
                    if len(years) >= 2:
                        if is_date(years[1]):
                            release_date = release_date + " - " + str(years[1])
                        else:
                            release_date = release_date + " - "
                elif is_date(re.sub('\([^\)]+\)', '', temp_date).strip()):
                    release_date = str(re.sub('\([^\)]+\)', '', temp_date).strip())
                else:
                    continue
            except:
                print("Date culprit: " + temp_date)

            # Technical details
            Camera = 'Camera'
            Cinematgrophy = 'Cinematographic Process'
            tech = bs(urlopen(tech_specs_url), 'html.parser')
            tech_content = tech.find('div', {'id':'technical_content'})
            table = tech_content.find('table', {'class':'dataTable labelValueTable'})
            
            specs = {}
            if table is not None:
                for row in table.find_all('tr'):
                    col1 = row.find('td', {'class':None}).text.strip()
                    col0 = row.find('td', {'class':'label'}).text.strip()
                    specs[col0] = col1
            
            # Display results
            genre = ""
            if tv_series:
                genre = "TV Series"
            else:
                genre = "Film"
            if Camera in specs:
                camera_det = ','.join([x.strip() for x in  specs[Camera].split('\n') if x.strip() != ''])
                if Cinematgrophy not in specs:
                    print("{}| {}| {}| [{}]| [{}]".format(film_name, release_date, genre, camera_det, ""))
                else:
                    cinema_process = camera_det = ','.join([x.strip() for x in  specs[Cinematgrophy].split('\n') if x.strip() != ''])
                    print("{}| {}| {}| [{}]| [{}]".format(film_name, release_date, genre, camera_det, cinema_process))
            else:
                print("{}| {}| {}| [{}]| [{}]".format(film_name, release_date, genre, "", ""))
                
        
        # Navigate to next page
        next_page = "https://www.imdb.com/search/title/?companies=co0041930&view=simple&sort=release_date,desc&start=" + str(page_count)
        page = urlopen(next_page)
        soup = bs(page, 'html.parser')

# Check for release date 
def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

if __name__ == "__main__":
    main()