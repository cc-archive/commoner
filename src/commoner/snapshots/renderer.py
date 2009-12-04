from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtWebKit import QWebPage

import time
import logging

QTAppInstance = QApplication([])

class TimeoutError(RuntimeError):
    pass
class LoadingError(RuntimeError):
    pass

class WebkitRenderer(QObject):

    # Initializes the QWebPage object and registers some slots
    def __init__(self):
        logging.debug("Initializing class %s", self.__class__.__name__)
        self._page = QWebPage()
        self.connect(self._page, SIGNAL("loadFinished(bool)"), self.__on_load_finished)
        self.connect(self._page, SIGNAL("loadStarted()"), self.__on_load_started)

        # The way we will use this, it seems to be unesseccary to have Scrollbars enabled
        self._page.mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        self._page.mainFrame().setScrollBarPolicy(Qt.Vertical, Qt.ScrollBarAlwaysOff)

        # Helper for multithreaded communication through signals 
        self.__loading = False
        self.__loading_result = False

    # Loads "url" and renders it.
    # Returns QImage-object on success.
    def render(self, url, width=0, height=0, timeout=10):
        logging.debug("render(%s, timeout=%d)", url, timeout)
        print "rendering..."
        # This is an event-based application. So we have to wait until
        # "loadFinished(bool)" raised.
        cancelAt = time.time() + timeout
        self._page.mainFrame().load(QUrl(url))
        while self.__loading:
            if timeout > 0 and time.time() >= cancelAt:
                print "Timed out."
                raise TimeoutError("Request timed out")
            QCoreApplication.processEvents()

        logging.debug("Processing result")

        if self.__loading_result == False:
            raise LoadingError("Failed to load %s" % url)

        # Set initial viewport (the size of the "window")
        size = self._page.mainFrame().contentsSize()
        if width > 0:
            size.setWidth(width)
        if height > 0:
            size.setHeight(height)
        self._page.setViewportSize(size)

        # Paint this frame into an image
        image = QImage(self._page.viewportSize(), QImage.Format_ARGB32)
        painter = QPainter(image)
        self._page.mainFrame().render(painter)
        painter.end()
        print "finished painting!"
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
