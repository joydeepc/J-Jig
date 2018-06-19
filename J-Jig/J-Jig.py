import wx
import os
import sys
import image_slicer
import random
from PIL import Image
import wx.html
import time
from zipfile import ZipFile
from StringIO import StringIO

aboutText = """<h1>J-Jig</h1><p><b>J-Jig</b> is a simple jigsaw puzzle game. To
open a picture, from File menu, select Open. Choose any picture from your
picture folder. Watch it carefully. When ready, click on Start in File menu. To
swap 2 pieces of picture blocks, click on first block to select it. The block
will be highlighted. Then click on second block. They will swap places. When
done, click on Done in File menu.<br />It is developed in <b>Python</b>
%(python)s and <b>wxPython</b> %(wxpy)s.<br /><br />Like it? Love it? All crap?
Please comment <a href="mailto:chalao.adda@gmail.com?Subject=J-Jig"
target="_top">Mail Me</a></p>"""

congratText = """<p><b>Congratulation!! You made it.</b><br /><br />Time Taken: <b>%(wxtm)s</b></p>"""
sorryText = """<p><b>Sorry, Not Yet Completed.</b></p>"""

# dataDir = os.getcwd() + "/Data"
# dataDir = os.getcwd()

def PilImageToWxImage(myPilImage):
    myWxImage = wx.EmptyImage(myPilImage.size[0], myPilImage.size[1])
#    myWxImage.SetData(myPilImage.convert('RGB').tostring())
    myWxImage.SetData(myPilImage.convert('RGB').tobytes())
    return myWxImage

def imageToPil(myWxImage):
    myPilImage = Image.new(
        'RGB', (myWxImage.GetWidth(), myWxImage.GetHeight()))
#    myPilImage.fromstring(myWxImage.GetData())
    myPilImage.frombytes(myWxImage.GetData())
    return myPilImage

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

zp = ZipFile(resource_path("Data.zip"), 'r')
zList = zp.namelist()

# MaxWidth = 1366; MaxHeight = 668
# For 6 X 6: MaxWidth = 222/tile; MaxHeight = 110/tile
# For 5 X 5: MaxWidth = 265/tile; MaxHeight = 130/tile

class HtmlWindow(wx.html.HtmlWindow):
    def __init__(self, parent, id, size=(600, 400)):
        wx.html.HtmlWindow.__init__(self, parent, id, size=size)
        if "gtk2" in wx.PlatformInfo:
            self.SetStandardFonts()

    def OnLinkClicked(self, link):
        wx.LaunchDefaultBrowser(link.GetHref())

class JHtmlWin(wx.Dialog):
    def __init__(self, parent, title, txt, imgD, hsize):
        wx.Dialog.__init__(self, parent, -1, title=title, size=(600, 400))
        self.txt = txt
        self.imgD = imgD
        self.hsize = hsize
        hwin = HtmlWindow(self, wx.ID_ANY, size=self.hsize)
        hwin.SetPage(self.txt)
        im = wx.EmptyImage(45, 45)
        imgc = wx.StaticBitmap(self, wx.ID_ANY, wx.BitmapFromImage(im))
        imgc.SetBitmap(wx.BitmapFromImage(self.imgD))
        b = wx.Button(self, wx.ID_OK, "OK")
        s = wx.BoxSizer(wx.VERTICAL)
        s.Add(hwin, 1, wx.EXPAND | wx.ALL | wx.ALIGN_CENTRE, 5)
        s.Add(imgc, 0, wx.ALL | wx.ALIGN_CENTRE, 5)
        s.Add(b, 0, wx.ALIGN_CENTER | wx.ALL, 5)
        self.SetSizerAndFit(s)
        s.Fit(self)
        self.Layout()

class MyPanel(wx.Panel):
    def __init__(self, parent, tn):
        wx.Panel.__init__(self, parent)
        self.tn = tn
        if self.tn == 36:
            ImgW = 222
            ImgH = 110
            rows = 6
            cols = 6
        else:
            ImgW = 265
            ImgH = 130
            rows = 5
            cols = 5
        pimg = wx.EmptyImage(ImgW, ImgH)
        self.ic = []
        for i in range(self.tn):
            self.ic.append(wx.StaticBitmap(self,
                                           i + 1,
                                           wx.BitmapFromImage(pimg),
                                           name="Pic" + str(i + 1)))
        hMainSizer = wx.BoxSizer(wx.HORIZONTAL)
        vGSSizer = wx.BoxSizer(wx.VERTICAL)
        gs = wx.GridSizer(rows, cols, 0, 0)
        for i in range(self.tn):
            gs.Add(self.ic[i], 0, wx.ALIGN_LEFT, 0)
        vGSSizer.Add(gs, 0, wx.ALL | wx.EXPAND, 5)
        hMainSizer.Add(vGSSizer, 0, wx.ALL | wx.EXPAND, 5)
        self.SetSizerAndFit(hMainSizer)
        hMainSizer.Fit(self)
        self.Refresh()
        self.Layout()

class Frame1(wx.Frame):

    def __init__(self, *args, **kwargs):
        kwargs["style"] = (wx.DEFAULT_FRAME_STYLE | wx.MAXIMIZE) & ~ \
            (wx.RESIZE_BORDER | wx.RESIZE_BOX | wx.MAXIMIZE_BOX)
        wx.Frame.__init__(self, *args, **kwargs)
        self.Bind(wx.EVT_CLOSE, self.OnExit)

        if zList[0] == "J-Jig.ico":
            self.SetIcon(wx.Icon(zList[0], wx.BITMAP_TYPE_ICO))
        self.ind = []
        self.bmpList = []
        self.bFirstTime = False
        self.picList = []
        self.tileNo = 25
        self.MaxImgW = 265
        self.MaxImgH = 130

        self.initUI()
        self.CreateStatusBar()
        self.panel1 = MyPanel(self, 25)
        msz = wx.BoxSizer()
        msz.AddStretchSpacer(1)
        msz.Add(self.panel1, 0, wx.ALIGN_CENTER)
        msz.AddStretchSpacer(1)
        self.SetSizerAndFit(msz)
        self.Layout()
        self.Center()
        self.Show()
        self.Maximize()

    def initUI(self):
        self.m_menubar = wx.MenuBar()
        self.m_file = wx.Menu()
        self.m_open = wx.MenuItem(
            self.m_file,
            wx.ID_ANY,
            "&Open",
            "Open a Picture",
            wx.ITEM_NORMAL)
        self.m_file.AppendItem(self.m_open)
        self.Bind(wx.EVT_MENU, self.OnOpen, self.m_open)
        self.m_file.AppendSeparator()
        self.m_start = wx.MenuItem(
            self.m_file,
            wx.ID_ANY,
            "&Start",
            "Starts J-Jig",
            wx.ITEM_NORMAL)
        self.m_file.AppendItem(self.m_start)
        self.Bind(wx.EVT_MENU, self.OnStart, self.m_start)
        self.m_start.Enable(False)
        self.m_done = wx.MenuItem(
            self.m_file,
            wx.ID_ANY,
            "&Done",
            "",
            wx.ITEM_NORMAL)
        self.m_file.AppendItem(self.m_done)
        self.Bind(wx.EVT_MENU, self.OnDone, self.m_done)
        self.m_done.Enable(False)
        self.m_file.AppendSeparator()
        self.m_exit = wx.MenuItem(
            self.m_file,
            wx.ID_ANY,
            "E&xit\tAlt-X",
            "Quits J-Jig",
            wx.ITEM_NORMAL)
        self.m_file.AppendItem(self.m_exit)
        self.Bind(wx.EVT_MENU, self.OnExit, self.m_exit)
        self.m_menubar.Append(self.m_file, "&File")
        self.m_option = wx.Menu()
        tile25 = self.m_option.AppendRadioItem(1001, "5 X 5")
        tile36 = self.m_option.AppendRadioItem(1002, "6 X 6")
        self.Bind(wx.EVT_MENU, self.OnPref, tile25)
        self.Bind(wx.EVT_MENU, self.OnPref, tile36)
        self.m_menubar.Append(self.m_option, "O&ption")
        self.m_option.Check(1001, True)
        self.m_help = wx.Menu()
        self.m_about = wx.MenuItem(
            self.m_help,
            wx.ID_ANY,
            "&About",
            "About J-Jig",
            wx.ITEM_NORMAL)
        self.m_help.AppendItem(self.m_about)
        self.Bind(wx.EVT_MENU, self.OnAbout, self.m_about)
        self.m_menubar.Append(self.m_help, "&Help")
        self.SetMenuBar(self.m_menubar)

    def OnPref(self, event):
        for item in self.m_option.GetMenuItems():
            if item.IsChecked():
                self.m_start.Enable(False)
                state = item.GetLabel()
                self.picList = []
                if state == "6 X 6":
                    self.tileNo = 36
                    self.MaxImgW = 222
                    self.MaxImgH = 110
                    self.SetStatusText("6 X 6 Game")
                else:
                    self.tileNo = 25
                    self.MaxImgW = 265
                    self.MaxImgH = 130
                    self.SetStatusText("5 X 5 Game")
                self.panel1.Hide()
                self.panel1 = MyPanel(self, self.tileNo)

    def OnOpen(self, event):
        wildcard = "Image Files (*.bmp,*.gif,*.jpg,*.png)|*.bmp;*.gif;*.jpg;*.JPG;*.png|" \
                   "All Files (*.*)|*.*"
        message = "Choose a Image File"
        dlg = wx.FileDialog(self,
                            message=message,
                            defaultDir=os.getcwd() + "/Images",
                            defaultFile="*.jpg",
                            wildcard=wildcard,
                            style=wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            picFile = dlg.GetFilename()
            self.SetStatusText(picFile)
            dirname = dlg.GetDirectory()
            pic = os.path.join(dirname, picFile)
            picName = resource_path(pic)
            wxImg = []
            self.picList = []
            tiles = image_slicer.slice(picName, self.tileNo, save=False)
            for tile in tiles:
                wxImg.append(
                    PilImageToWxImage(tile.image).Scale(self.MaxImgW, self.MaxImgH))
            for i in range(len(wxImg)):
                self.panel1.ic[i].SetBitmap(wx.BitmapFromImage(wxImg[i]))
                self.picList.append("Pic" + str(i + 1))
            self.panel1.Refresh()
            self.m_start.Enable(True)
        dlg.Destroy()

    def OnDone(self, evt):
        self.bmpList = []
        for i in range(len(self.panel1.ic)):
            self.bmpList.append(self.panel1.ic[i].GetName())
        if self.picList == self.bmpList:
            self.tmr.Stop()
            self.SetStatusText("Congratulation! You have WON !!!")
            v = {}
            etime = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.ct))
            v["wxtm"] = etime
            txt = congratText % v
            if zList[2] == "smiley2.jpg":
                img = wx.ImageFromStream(StringIO(zp.read(zList[2]))).Scale(45, 45)
            hsize = (200, 200)
            dlg = JHtmlWin(self, "Congratulation!", txt, img, hsize)
            dlg.ShowModal()
            dlg.Destroy()
            self.m_done.Enable(False)
            self.m_start.Enable(True)
        else:
            txt = sorryText
            if zList[3] == "smiley3.jpg":
                img = wx.ImageFromStream(StringIO(zp.read(zList[3]))).Scale(45, 45)
            hsize = (200, 100)
            dlg = JHtmlWin(self, "Sorry", txt, img, hsize)
            dlg.ShowModal()
            dlg.Destroy()
            self.bmpList = []
            self.m_start.Enable(False)
            self.m_done.Enable(True)
        self.panel1.Refresh()

    def OnStart(self, evt):
        self.bmpList = []
        for x in range(len(self.panel1.ic)):
            self.panel1.ic[x].Bind(wx.EVT_LEFT_DOWN, self.OnClick)
            r = random.randint(0, len(self.panel1.ic) - 1)
            tmp1 = self.panel1.ic[x].GetBitmap()
            tmp2 = self.panel1.ic[r].GetBitmap()
            a = self.panel1.ic[x].GetName()
            b = self.panel1.ic[r].GetName()
            self.panel1.ic[x].SetName(b)
            self.panel1.ic[r].SetName(a)
            self.panel1.ic[x].SetBitmap(tmp2)
            self.panel1.ic[r].SetBitmap(tmp1)
        self.bFirstTime = True
        self.panel1.Refresh()
        self.tmr = wx.Timer(self, -1)
        self.Bind(wx.EVT_TIMER, self.OnUpdate, self.tmr)
        self.ct = time.time()
        self.tmr.Start(1000)
        self.m_start.Enable(False)
        self.m_done.Enable(True)

    def OnUpdate(self, evt):
        st = time.strftime("%H:%M:%S", time.gmtime(time.time() - self.ct))
        self.SetStatusText(st)

    def OnClick(self, evt):
        o = evt.GetEventObject()
        ix = self.panel1.ic.index(o)

        if self.bFirstTime:
            self.bmpList = []
            self.ind = []
            self.ind.append(ix)
            self.bmpList.append(self.panel1.ic[ix].GetBitmap())
            bmp = self.panel1.ic[ix].GetBitmap()
            pilimg = imageToPil(wx.ImageFromBitmap(bmp))
            k = 1.5
            out = Image.eval(pilimg, lambda x: int(x * k))
            sbmp = wx.BitmapFromImage(PilImageToWxImage(out))
            self.panel1.ic[ix].SetBitmap(sbmp)
            self.bFirstTime = False
        else:
            self.bmpList.append(self.panel1.ic[ix].GetBitmap())
            self.ind.append(ix)
            bmp1 = self.bmpList[0]
            bmp2 = self.bmpList[1]
            name1 = self.panel1.ic[self.ind[0]].GetName()
            name2 = self.panel1.ic[self.ind[1]].GetName()
            self.panel1.ic[self.ind[0]].SetName(name2)
            self.panel1.ic[self.ind[1]].SetName(name1)
            self.panel1.ic[self.ind[0]].SetBitmap(bmp2)
            self.panel1.ic[self.ind[1]].SetBitmap(bmp1)
            self.bFirstTime = True
            self.bmpList = []
            self.ind = []
        self.panel1.Refresh()

    def OnExit(self, event):
        zp.close()
        self.Destroy()

    def OnAbout(self, event):
        v = {}
        v["python"] = sys.version.split()[0]
        v["wxpy"] = wx.VERSION_STRING
        txt = aboutText % v
        if zList[1] == "smiley1.jpg":
            img = wx.ImageFromStream(StringIO(zp.read(zList[1]))).Scale(45, 45)
        hsize = (400, 300)
        dlg = JHtmlWin(self, "About J-Jig", txt, img, hsize)
        dlg.ShowModal()
        dlg.Destroy()

if __name__ == "__main__":
    a = wx.App(0)
    f = Frame1(None, -1, "J-Jig")
    a.MainLoop()
