import wx
import sys
import datetime
import requests

from pybliometrics.scopus import ScopusSearch, AuthorRetrieval, AbstractRetrieval

API_KEY = '871232b0f825c9b5f38f8833dc0d8691'

#URL = 'http://mumtmis.herokuapp.com/research/api/articles'
URL = 'http://localhost:5000/research/api/articles'

QUERY = 'AFFILORG ( "Faculty of Medical Technology"  "Mahidol University" )  AND  AFFILCOUNTRY ( thailand ) PUBYEAR = {}'


class MainPanel(wx.Panel):
    def __init__(self, parent):
        super(MainPanel, self).__init__(parent=parent)
        download_btn = wx.Button(self, label='Download')
        download_btn.Bind(wx.EVT_BUTTON, self.download)
        self.search_box = wx.TextCtrl(self,
                                      size=(300, 100),
                                      style=wx.TE_MULTILINE | wx.TE_READONLY)
        self.search_box.SetValue(QUERY.format(datetime.datetime.now().year))
        search_lbl = wx.StaticText(self, label="Search Query")
        status_lbl = wx.StaticText(self, label='Downloading')
        self.total_lbl = wx.StaticText(self, label='')
        self.progress_lbl = wx.StaticText(self, label='')
        self.progress_bar = wx.Gauge(self)
        self.year_box = wx.TextCtrl(self)
        self.year_box.SetValue(str(datetime.datetime.now().year))
        self.year_box.SetFocus()
        self.year_box.Bind(wx.EVT_TEXT, self.change_year)
        search_sizer = wx.FlexGridSizer(2, 5, 5)
        search_sizer.Add(search_lbl, flag=wx.ALL)
        search_sizer.Add(self.search_box, proportion=1, flag=wx.ALL | wx.EXPAND)
        search_sizer.Add(wx.StaticText(self, label="Year"))
        search_sizer.Add(self.year_box)
        search_sizer.Add(wx.StaticText(self, label='Total'))
        search_sizer.Add(self.total_lbl)
        search_sizer.Add(status_lbl)
        search_sizer.Add(self.progress_lbl)
        search_sizer.Add(wx.StaticText(self, label='Complete'))
        search_sizer.Add(self.progress_bar)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(download_btn)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(search_sizer, flag=wx.ALL | wx.EXPAND, border=5)
        vsizer.Add(button_sizer, flag=wx.ALL | wx.CENTER, border=5)
        vsizer.Add((-1, 20))
        self.SetSizer(vsizer)
        self.Fit()

    def download(self, event):
        results = ScopusSearch(self.search_box.GetValue(), subscriber=True, verbose=True)
        self.total_lbl.SetLabel(str(results.get_results_size()))
        self.progress_bar.SetRange(results.get_results_size())
        for n, doc in enumerate(results.results, start=1):
            try:
                self.progress_lbl.SetLabel(doc.eid)
                abstract = AbstractRetrieval(doc.eid, view='FULL')
            except:
                self.progress_lbl.SetLabel(doc.eid + ' failed to download.')

            subject_areas = []
            for subj in abstract.subject_areas:
                subject_areas.append({
                    'area': subj.area,
                    'code': subj.code,
                    'abbreviation': subj.abbreviation,
                })
            authors = []
            for aid in doc.author_ids.split(';'):
                author = AuthorRetrieval(aid)
                authors.append({
                    'author_id': aid,
                    'firstname': author.given_name,
                    'lastname': author.surname,
                    'h_index': author.h_index,
                    'link': author.scopus_author_link,
                    'indexed_name': author.indexed_name,
                })

            resp = requests.post(URL, json={
                'scopus_id': doc.eid,
                'scopus_link': abstract.scopus_link,
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
                self.progress_lbl.SetLabel(doc.eid + ' done.')
            else:
                self.progress_lbl.SetLabel(doc.eid + ' failed to save data.')
            self.progress_bar.SetValue(n)
        self.progress_lbl.SetLabel('Finished.')


    def change_year(self, event):
        self.search_box.SetValue(QUERY.format(self.year_box.GetValue()))


class MainFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        super(MainFrame, self).__init__(*args, **kwargs)
        panel = MainPanel(self)

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(panel)
        self.SetSizer(sizer)
        self.Fit()



if __name__ == '__main__':
    app = wx.App()
    main_frame = MainFrame(None, title='SCOPUS Downloader', size=(600,700))
    main_frame.Show()
    app.MainLoop()