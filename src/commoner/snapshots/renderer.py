from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage

import time
import logging

LOG_FILENAME = '/tmp/snapshots.out'
logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)

QTAppInstance = QApplication([])

class TimeoutError(RuntimeError):
    pass
class LoadingError(RuntimeError):
    pass
class InvalidURLError(RuntimeError):
    pass

class CCQWebPage(QWebPage):
    def __init__(self, parent=None):
        super(CCQWebPage, self).__init__(parent)
    def userAgentForUrl(self, url):
        return 'CC Web Citation http://wiki.creativecommons.org/Webcitations'

# Class for Website-Rendering. Uses QWebPage, which
# requires a running QtGui to work.
class WebkitRenderer(QObject):
 
    # Initializes the QWebPage object and registers some slots
    def __init__(self):
        QObject.__init__(self)
        logging.debug("Initializing class %s", self.__class__.__name__)
        self._page = CCQWebPage()
        self.connect(self._page, SIGNAL("loadFinished(bool)"), self.__on_load_finished)
        self.connect(self._page, SIGNAL("loadStarted()"), self.__on_load_started)
        self.connect(self._page.networkAccessManager(), SIGNAL("sslErrors(QNetworkReply *,const QList<QSslError>&)"), self.__on_ssl_errors)
 
        # The way we will use this, it seems to be unesseccary to have Scrollbars enabled
        self._page.mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self._page.mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)
 
        # Helper for multithreaded communication through signals
        self.__loading = False
        self.__loading_result = False
 
    # Loads "url" and renders it.
    # Returns QImage-object on success.
    def render(self, url, width=0, height=0, timeout=0):

        print "Rendering: %s" % url
        
        logging.debug("render(%s, timeout=%d)", url, timeout)
 
        # This is an event-based application. So we have to wait until
        # "loadFinished(bool)" raised.
        cancelAt = time.time() + timeout

        qturl = QUrl(url, QUrl.TolerantMode)
        if not qturl.isValid():
            raise InvalidURLError("Invalid URL: %s" % url)

        # set the size now so Qt doesn't try to interpret the content size
        # and render something gigantic
        size = self._page.mainFrame().contentsSize()
        size.setWidth(1024)
        self._page.setViewportSize(size)
        
        self._page.mainFrame().load(qturl)
        while self.__loading:
            if timeout > 0 and time.time() >= cancelAt:
                raise TimeoutError("Request timed out")
            QCoreApplication.processEvents()
 
        logging.debug("Processing result")
 
        if self.__loading_result == False:
            raise LoadingError("Failed to load %s" % url)
 
        # Set initial viewport (the size of the "window")
        size = self._page.mainFrame().contentsSize()
        logging.debug("contentsSize: %s", size)
        if width > 0:
            size.setWidth(width)
        if height > 0:
            size.setHeight(height)
        
        self._page.setViewportSize(size)
 
        # Paint this frame into an image
        logging.debug("Painting result")
        
        image = QImage(self._page.viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)

        self.connect(self._page, SIGNAL("loadStarted()"), self.__on_load_started)
        
        self._page.mainFrame().render(painter)
        painter.end()
 
        return image
 
    # Eventhandler for "loadStarted()" signal
    def __on_load_started(self):
        logging.debug("loading started")
        self.__loading = True
 
    # Eventhandler for "loadFinished(bool)" signal
    def __on_load_finished(self, result):
        logging.debug("loading finished with result %s", result)
        self.__loading = False
        self.__loading_result = result
 
    # Eventhandler for "sslErrors(QNetworkReply *,const QList<QSslError>&)" signal
    def __on_ssl_errors(self, reply, errors):
        logging.warn("ssl error")
        #self.__loading = False
        #self.__loading_result = result
        reply.ignoreSslErrors()
