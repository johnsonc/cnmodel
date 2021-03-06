#!/usr/bin/python
from __future__ import print_function
__author__ = 'pbmanis'

"""
Basic test of cnmodel decorator on simple cell
Users LC_bushy.hoc and XM13 mechanisms.

"""

import sys
import numpy as np
import cnmodel.cells as cells
import cnmodel.decorator as Decorator
from cnmodel.util import pyqtgraphPlotHelpers as PH
from cnmodel.protocols import IVCurve
import pyqtgraph as pg
import timeit


class F5():
    def __init__(self, filename):
        # build plotting area
        #
        self.filename = filename
        self.iv = IVCurve()  # use standard IVCurve here...
        self.temperature = 34
        self.initdelay = 150.
        
    def run(self):
        self.post_cell = cells.Bushy.create(morphology=self.filename, decorator=Decorator,
                    species='mouse', modelType='XM13')
        self.post_cell.set_temperature(float(self.temperature))
        self.post_cell.set_d_lambda(freq=2000.)  # necessary to ensure appropriate spatial 
        self.iv.reset()
        irange = self.post_cell.i_test_range
        irange = {'pulse': (-0.6, 1.1, 0.2)}
        self.durs = (self.initdelay+20., 100., 50.)
        self.iv.run(irange, self.post_cell, durs=self.durs, temp=float(self.temperature),
                initdelay=self.initdelay)
    
    def plot(self):
        pg.setConfigOption('background', 'w')  # set background to white
        pg.setConfigOption('foreground', 'k')
        self.app = pg.mkQApp()

        wintitle = 'test_decorator'
        self.view = pg.GraphicsView()
        self.layout = pg.GraphicsLayout()  #(border=(100,100,100))
        self.view.setCentralItem(self.layout)
        self.view.resize(800, 600)
        self.view.show()
        self.plots = {}
        nr1 = 6
        nc = 10
        for i in range(1, nr1):
            self.plots['p%d' % i] = None
        for i in range(1,nr1+1):
            self.layout.addLayout(row=i, col=nc)
        for i in range(1,nc + 1):
            self.layout.addLayout(row=nr1+2, col = i)

        self.plots['p1'] = self.layout.addPlot(row=1, col=1, 
                rowspan=6, colspan=9, labels={'left': 'V (mV)', 'bottom': 'Time (ms)'})
        self.plots['p2'] = self.layout.addPlot(row=7, col=1,
                rowspan=1,  colspan=9, labels={'left': 'I (nA)', 'bottom': 'Time (ms)'})

        for k in range(len(self.iv.voltage_traces)):
            self.plots['p1'].plot(self.iv.time_values, np.array(self.iv.voltage_traces[k]), pen=pg.mkPen('k', width=0.75))
            self.plots['p2'].plot(self.iv.time_values, np.array(self.iv.current_traces[k]), pen=pg.mkPen('k', width=0.75))
        self.plots['p1'].setRange(xRange=(0., np.sum(self.durs) - self.initdelay), yRange=(-160., 40.))
        self.plots['p2'].setRange(xRange=(0., np.sum(self.durs) - self.initdelay), yRange=(-1, 1))
        PH.noaxes(self.plots['p1'])
        PH.calbar(self.plots['p1'], calbar=[125., -120., 10., 20.], unitNames={'x': 'ms', 'y': 'mV'})
        PH.noaxes(self.plots['p2'])
        PH.calbar(self.plots['p2'], calbar=[125, 0.1, 0., 0.5], unitNames={'x': 'ms', 'y': 'nA'})

        text = (u"{0:2d}\u00b0C {1:.2f}-{2:.2f} nA".format(
                int(self.temperature), np.min(self.iv.current_cmd), np.max(self.iv.current_cmd)))
        ti = pg.TextItem(text, anchor=(1, 0))
        ti.setFont(pg.QtGui.QFont('Arial', 9))
        ti.setPos(120., -120.)
        self.plots['p1'].addItem(ti)


if __name__ == '__main__':
    fig5 = F5('examples/LC_bushy.hoc')
    start_time = timeit.default_timer()
    fig5.run()
    elapsed = timeit.default_timer() - start_time
    print ('Elapsed time for simulation: %f' % (elapsed))
    fig5.plot()
    if sys.flags.interactive == 0:
        pg.QtGui.QApplication.exec_()
    
    
