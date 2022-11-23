import sys
import requests

from pybliometrics.scopus import ScopusSearch, AuthorRetrieval, AbstractRetrieval

# add radio button for switching remote server
URL = 'http://mumtmis.herokuapp.com/research/api/articles'
# URL = 'http://127.0.0.1:5000/research/api/articles'

QUERY = ('AFFIL ( "Faculty of Medical Technology" AND "Mahidol university" )'
        '  AND  AFFILCOUNTRY ( thailand ) PUBYEAR = {}')


def main(year):
    query = QUERY.format(year)
    results = ScopusSearch(query,
                           subscriber=False,
                           verbose=True,
                           refresh=True)

    print('Total is {}'.format(results.get_results_size()))
    print('Fetching article data..')

    for n, doc in enumerate(results.results, start=1):
        try:
            abstract = AbstractRetrieval(doc.eid, view='META', refresh=True)
        except Exception as e:
            print(e)
            continue

        subject_areas = []
        if abstract.subject_areas:
            for subj in abstract.subject_areas:
                subject_areas.append({
                    'area': subj.area,
                    'code': subj.code,
                    'abbreviation': subj.abbreviation,
                })
        authors = []
        if abstract.authors:
            for aid in doc.author_ids.split(';'):
                author = AuthorRetrieval(aid)
                affiliation = None
                if author.affiliation_current:
                    affiliation = author.affiliation_current[0]
                authors.append({
                    'author_id': aid,
                    'firstname': author.given_name,
                    'lastname': author.surname,
                    'h_index': author.h_index,
                    'link': author.scopus_author_link,
                    'indexed_name': author.indexed_name,
                    'afid': affiliation.id if affiliation else None,
                    'afname': affiliation.preferred_name if affiliation else None,
                    'country': affiliation.country if affiliation else None
                })
        try:
            resp = requests.post(URL, json={
                'scopus_id': doc.eid,
                'scopus_link': abstract.scopus_link,
                'publication_name': abstract.publicationName,
                'subject_areas': subject_areas,
                'title': doc.title,
                'doi': doc.doi,
                'citedby_count': doc.citedby_count,
                'abstract': doc.description,
                'cover_date': doc.coverDate,
                'authors': authors,
                'author_names': doc.author_names,
                'author_afids': doc.author_afids,
                'afid': doc.afid,
                'affiliation_country': doc.affiliation_country,
                'affilname': doc.affilname,
            })
            if resp.status_code != 200:
                print('{}) {} failed.'.format(n, doc.title[:30]))
            else:
                print('{}) {} done.'.format(n, doc.title[:30]))
        except:
            continue
    print('Done.')


if __name__ == '__main__':
    year = sys.argv[1]
    main(year)
