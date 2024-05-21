from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, \
	QStyle, QSlider, QFileDialog, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import Qt, QUrl, QTimer
import sys

class ClickableSlider(QSlider):
	def mousePressEvent(self, event):
		super().mousePressEvent(event)
		if event.button() == Qt.LeftButton:
			value = int(self.minimum() + ((self.maximum() - self.minimum()) * event.x()) / self.width())
			self.setValue(value)
			self.sliderMoved.emit(value)

class Window(QWidget):
	def __init__(self):
		super().__init__()

		self.setWindowIcon(QIcon("player.ico"))
		self.setWindowTitle("My Media Player")
		self.setGeometry(350, 100, 700, 500)
		self.setAcceptDrops(True)

		self.hidden = False

		global hbox
		hbox = QHBoxLayout()

		self.setFocusPolicy(Qt.StrongFocus)
		self.create_player()

	def create_player(self):
		self.mediaPlayer = QMediaPlayer(None, QMediaPlayer.VideoSurface)

		videowidget = QVideoWidget()

		self.openBtn = QPushButton('Open Video')
		self.openBtn.clicked.connect(self.open_file)

		self.playBtn = QPushButton()
		self.playBtn.setEnabled(False)
		self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))
		self.playBtn.clicked.connect(self.play_video)

		self.slider = ClickableSlider(Qt.Horizontal)
		self.slider.setRange(0, 0)
		self.slider.sliderMoved.connect(self.set_position)

		slider_style = """
			QSlider::groove:horizontal {
			border: 1px solid #999999;
			height: 8px;
			background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #B1B1B1, stop:1 #c4c4c4);
			margin: 2px 0;
			}

			QSlider::handle:horizontal {
			background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #b4b4b4, stop:1 #8f8f8f);
			border: 1px solid #5c5c5c;
			width: 18px;
			margin: -2px 0;
			border-radius: 3px;
			}
		"""

		self.slider.setStyleSheet(slider_style)

		self.timeLabel = QLabel("00:00:00")
		self.timeLabel.setFixedWidth(80)

		hbox.setContentsMargins(0, 0, 0, 0)
		hbox.addWidget(self.openBtn)
		hbox.addWidget(self.playBtn)
		hbox.addWidget(self.timeLabel)
		hbox.addWidget(self.slider)

		vbox = QVBoxLayout()
		vbox.addWidget(videowidget)
		vbox.addLayout(hbox)

		self.setLayout(vbox)
		self.mediaPlayer.setVideoOutput(videowidget)

		self.mediaPlayer.stateChanged.connect(self.mediastate_changed)
		self.mediaPlayer.positionChanged.connect(self.position_changed)
		self.mediaPlayer.durationChanged.connect(self.duration_changed)

	def keyPressEvent(self, event):
		if event.key() == Qt.Key_Space:
			self.play_video()
		elif event.key() == Qt.Key_Right:
			self.mediaPlayer.setPosition(self.mediaPlayer.position() + 5000)
			self.set_duration_title(self.format_time(self.mediaPlayer.position()))
		elif event.key() == Qt.Key_Left:
			self.mediaPlayer.setPosition(self.mediaPlayer.position() - 5000)
			self.set_duration_title(self.format_time(self.mediaPlayer.position()))
		elif event.key() == Qt.Key_Up:
			self.mediaPlayer.setVolume(self.mediaPlayer.volume() + 5)
			self.set_volume_title(self.mediaPlayer.volume())
		elif event.key() == Qt.Key_Down:
			self.mediaPlayer.setVolume(self.mediaPlayer.volume() - 5)
			self.set_volume_title(self.mediaPlayer.volume())

	def open_file(self):
		filename, _ = QFileDialog.getOpenFileName(self, "Open Video")
		if filename:
			self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filename)))
			self.playBtn.setEnabled(True)

	def play_video(self):
		if self.mediaPlayer.state() == QMediaPlayer.PlayingState:
			self.mediaPlayer.pause()
		else:
			self.mediaPlayer.play()

	def mediastate_changed(self, state):
		if state == QMediaPlayer.PlayingState:
			self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPause))
		else:
			self.playBtn.setIcon(self.style().standardIcon(QStyle.SP_MediaPlay))

	def position_changed(self, position):
		self.slider.setValue(position)
		self.timeLabel.setText(self.format_time(position))
	   

	def format_time(self, ms):
		seconds = int(ms / 1000)
		minutes = int(seconds / 60)
		hours = int(minutes / 60)
		minutes = minutes % 60
		seconds = seconds % 60
		return f"{hours:02}:{minutes:02}:{seconds:02}"

	def duration_changed(self, duration):
		self.slider.setRange(0, duration)

	def set_position(self, position):
		self.mediaPlayer.setPosition(position)

	def set_volume_title(self, volume):
		self.setWindowTitle(f"Volume {volume}%")
		QTimer.singleShot(300, lambda: self.setWindowTitle("My Media Player"))

	def set_duration_title(self, duration):
		self.setWindowTitle(f"Duration {duration}")
		QTimer.singleShot(300, lambda: self.setWindowTitle("My Media Player"))

	def dragEnterEvent(self, e):
		if e.mimeData().hasUrls():
			e.accept()
		else:
			e.ignore()

	def dropEvent(self, e):
		urls = e.mimeData().urls()
		if urls and len(urls) > 0:
			url = urls[0]
			if url.isLocalFile():
				filepath = url.toLocalFile()
				self.load_video(filepath)

	def load_video(self, filepath):
		self.mediaPlayer.setMedia(QMediaContent(QUrl.fromLocalFile(filepath)))
		self.playBtn.setEnabled(True)
		self.play_video()

app = QApplication(sys.argv)
app.setStyle('QtCurve')
window = Window()
window.show()
sys.exit(app.exec_())
