import wx
import sys
import datetime

from pybliometrics.scopus import ScopusSearch

API_KEY = '871232b0f825c9b5f38f8833dc0d8691'

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
        self.year_box = wx.TextCtrl(self)
        self.year_box.SetValue(str(datetime.datetime.now().year))
        self.year_box.SetFocus()
        self.year_box.Bind(wx.EVT_TEXT, self.change_year)
        self.output_box = wx.TextCtrl(self, size=(600, 200),
                                      style=wx.TE_MULTILINE | wx.TE_READONLY | wx.VSCROLL)
        search_sizer = wx.FlexGridSizer(2, 5, 5)
        search_sizer.Add(search_lbl, flag=wx.ALL)
        search_sizer.Add(self.search_box, proportion=1, flag=wx.ALL | wx.EXPAND)
        search_sizer.Add(wx.StaticText(self, label="Year"))
        search_sizer.Add(self.year_box)
        search_sizer.Add(wx.StaticText(self, label="Output"))
        search_sizer.Add(self.output_box)
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        button_sizer.Add(download_btn)
        vsizer = wx.BoxSizer(wx.VERTICAL)
        vsizer.Add(search_sizer, flag=wx.ALL | wx.EXPAND, border=5)
        vsizer.Add(button_sizer, flag=wx.ALL | wx.CENTER, border=5)
        vsizer.Add((-1, 20))
        self.SetSizer(vsizer)
        self.Fit()
        sys.stdout = self.output_box

    def download(self, event):
        results = ScopusSearch(self.search_box.GetValue(), subscriber=True, verbose=True)
        print('Total articles = {}'.format(results.get_results_size()))

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