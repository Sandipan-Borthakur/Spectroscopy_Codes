import matplotlib.pyplot as plt
import numpy as np
from astropy.io import fits

class draggable_lines:
    def __init__(self, ax, X, color, picker):
        self.ax = ax
        self.c = ax.get_figure().canvas
        self.X = X
        self.color = color
        x = X
        self.line = ax.axvline(x, picker = picker, c = self.color)
        self.ax.add_line(self.line)
        self.c.draw_idle()
        self.sid = self.c.mpl_connect('pick_event', self.clickonline)

    def clickonline(self, event):
        if event.artist == self.line:
            print("line selected ", event.artist)
            self.follower = self.c.mpl_connect("motion_notify_event", self.followmouse)
            self.releaser = self.c.mpl_connect("button_press_event", self.releaseonclick)

    def followmouse(self, event):
        self.line.set_xdata([event.xdata, event.xdata])
        self.c.draw_idle()

    def releaseonclick(self, event):
        self.X = self.line.get_xdata()[0]
        self.c.mpl_disconnect(self.releaser)
        self.c.mpl_disconnect(self.follower)

# fig = plt.figure()
# ax = fig.add_subplot()
#
# data = fits.getdata('E:/PRL_Vishal_sir/For interview/R500_blue/Spectra/newnova_R500_blue.fits')[0]
# spec = np.sum(data,axis=1)
# ind = np.where(spec==np.max(spec))[0]
# Tlines = []
# for i in range(1):
#     for j in range(-1,3,2):
#         Tlines.append(draggable_lines(ax, len(spec)/6 + j*5, 'b',10))
# ax.plot(spec)
# plt.show()
# print(Tlines[1].X)