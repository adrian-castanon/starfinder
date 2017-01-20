#!/usr/bin/env python

import wx
from astropy.io import fits
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_wxagg import FigureCanvasWxAgg as FigureCanvas
from matplotlib.figure import Figure
from astropy.wcs import WCS
    
class Frame(wx.Frame):
      
    def __init__(self, parent, title):
        wx.Frame.__init__(self, None, -1, title=title, size=(1000,1000)) #Creates the frame
        self.Show(True) #Shows the frame
        
        self.Toolbar() # Preparing for the toolbar
        
        # Setting up the menu.
        filemenu= wx.Menu()
        
        #The different buttons in the menu
        menuAbout = filemenu.Append(wx.ID_ANY, "&About"," Information about this program")
        menuOpen = filemenu.Append(wx.ID_ANY, "&Open", " Open text file")
        menuExit = filemenu.Append(wx.ID_ANY,"E&xit"," Terminate the program")

        # Creating the menubar.
        menuBar = wx.MenuBar()
        menuBar.Append(filemenu,"&File") # Adding the "filemenu" to the MenuBar
        self.SetMenuBar(menuBar)  # Adding the MenuBar to the Frame content.
        
        # Set events.
        self.Bind(wx.EVT_MENU, self.OnAbout, menuAbout)
        self.Bind(wx.EVT_MENU, self.OnExit, menuExit)
        self.Bind(wx.EVT_MENU, self.OnOpen, menuOpen)
        
    
    def OnAbout(self,e):
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Starfinder was created by a young student traumatized by IRAF.", "About Starfinder", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
    def Toolbar(self): #The different buttons in the toolbar
        toolbar = self.CreateToolBar()
        finder = toolbar.AddLabelTool(wx.ID_ANY, '&Finder', wx.Bitmap('finder.jpg').ConvertToImage().Rescale(height=30, width=30).ConvertToBitmap())
        paint = toolbar.AddLabelTool(wx.ID_ANY, "&Paint",wx.Bitmap('paint.jpg').ConvertToImage().Rescale(height=30, width=30).ConvertToBitmap())
        export = toolbar.AddLabelTool(wx.ID_ANY, "&Export",wx.Bitmap('export.png').ConvertToImage().Rescale(height=30, width=30).ConvertToBitmap())
        save = toolbar.AddLabelTool(wx.ID_ANY, "&Save",wx.Bitmap('save.png').ConvertToImage().Rescale(height=30, width=30).ConvertToBitmap())
        resize = toolbar.AddLabelTool(wx.ID_ANY, "&Resize",wx.Bitmap('resize.png').ConvertToImage().Rescale(height=30, width=30).ConvertToBitmap())

        toolbar.Realize()
        
        self.Bind(wx.EVT_TOOL, self.OnFinder, finder)
        self.Bind(wx.EVT_TOOL, self.ComingSoon, paint)
        self.Bind(wx.EVT_TOOL, self.OnExport, export)
        self.Bind(wx.EVT_TOOL, self.ComingSoon, save)
        self.Bind(wx.EVT_TOOL, self.ComingSoon, resize)
        
        self.Centre()
        self.Show(True)
        
    def OnExit(self,e): #Close the program
        self.Close(True)  # Close the frame.
            
    def OnOpen(self, e): #Open a file
        dialog = wx.FileDialog(None, "Choose a file", wildcard='*.fits', style=wx.OPEN) #We can open only fits files
        if dialog.ShowModal() == wx.ID_OK:
            self.filename = dialog.GetFilename() #Gets the name of the file we want to open
        dialog.Destroy() 
        
        self.image_data = fits.getdata(self.filename, ext=0) #Gets the picture of the fits file
        
        hdulist = fits.open(self.filename) #Open the header of the fits file        
        header = hdulist['PRIMARY'].header
        hdulist.close() #Close the header of the fits file
        wcs = WCS(header)
        fig = plt.figure()
        ax = fig.add_axes([0.1, 0.1, 0.8, 0.8], projection=wcs)
        ax.set_xlabel('RA')
        ax.set_ylabel('Dec')
        ax.imshow(self.image_data, cmap='gist_heat',origin='lower')
        ra = ax.coords[0]
        ra.set_major_formatter('hh:mm:ss')
        dec = ax.coords[1]
        dec.set_major_formatter('dd:mm:ss');    
        self.figure = Figure()
        self.axes = self.figure.add_subplot(111)
        self.canvas = FigureCanvas(self, -1, fig) #Printing the figure
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.canvas, 1, wx.LEFT | wx.TOP | wx.EXPAND)
        self.SetSizer(self.sizer)
        self.Fit()
        
        
    def OnFinder(self, e):
        x = self.image_data.shape #This gives us the size of the matrix that makes image_dat
        a = x[0]
        b = x[1]
        mini=self.image_data[:,:].min() #Absolute minimum and maximum of the picture
        maxi=self.image_data[:,:].max()
        c = self.image_data #This strange thing is to add 10 columns and 10 files of 0s, because we suppose the radius of the stars in the picture are small or equal to 10
        d = np.append(c,np.zeros([a,10]),1)
        f = d.T
        d = np.append(f,np.zeros([a+10,10]),1)
        c = d.T
        maxim = maxi
        self.stars2 = []
        while maxim >= (maxi-mini): #This allows us to find the maximum we have in the picture, and we will make them disappear from a temporary variable
            for i in range(a):
                for j in range(b):
                    if c[i,j] == maxim:
                        z=[i,j]
                        stars = self.stars2
                        self.stars2 = np.concatenate((stars, z),axis=0) #The array of positions
                        for k in range(20):
                            for l in range(20):
                                c[i-10+k,j-10+l]=0 #This makes the stars that have been found disappear
            maxim = c[:,:].max() #After making disappear the found stars, we recalculate the maximum and repeat until we get out of the loop
        
    def OnExport(self, e):  #This allows us to export the positions of the stars
        dialog = wx.FileDialog(None, "Choose a name", wildcard='*.csv', style=wx.OPEN) #We need to choose an already created .csv blank file
        if dialog.ShowModal() == wx.ID_OK:
            self.exportar = dialog.GetFilename()
        dialog.Destroy() 
        exportar = open(self.exportar, 'w') #We open the file to write
        for i in range(len(self.stars2)/2):
            print >>exportar, self.stars2[2*i], self.stars2[2*i+1], "\n" #We write the star coordinates in the matrix two by two
        exportar.close()
        
    def ComingSoon(self,e): #Don't lose the hope, they will be finished, but not on time
        # A message dialog box with an OK button. wx.OK is a standard ID in wxWidgets.
        dlg = wx.MessageDialog( self, "Coming soon", "Not working yet", wx.OK)
        dlg.ShowModal() # Show it
        dlg.Destroy() # finally destroy it when finished.
        
app = wx.App(0)
frame = Frame(None, 'Starfinder')
app.MainLoop()  