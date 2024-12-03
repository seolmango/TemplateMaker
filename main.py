import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLineEdit, QLabel, QFileDialog, QListWidget, QDialog, QSpinBox,
    QTextEdit, QCheckBox
)
from PyQt5.QtCore import QTimer
from Maker import title_page, mood_page, list_page, review_page
import pickle
import os, sys

class TrackDialog(QDialog):
    def __init__(self, disc, order, parent=None):
        super().__init__(parent)
        self.setWindowTitle("트랙 데이터")
        self.resize(400, 300)

        self.layout = QFormLayout(self)

        # 트랙 정보 입력 받기
        self.disc_number = QSpinBox()
        self.disc_number.setMinimum(1)
        self.disc_number.setValue(disc)
        self.track_order = QSpinBox()
        self.track_order.setMinimum(1)
        self.track_order.setValue(order)
        self.track_title = QLineEdit()
        self.is_title_track = QCheckBox("Title")

        # 상세 리뷰
        self.review_checkbox = QCheckBox("상세 리뷰 작성")
        self.review_text = QTextEdit()
        self.review_text.setPlaceholderText("상세 리뷰 작성")
        self.review_text.setVisible(False)

        self.review_checkbox.stateChanged.connect(
            lambda: self.review_text.setVisible(self.review_checkbox.isChecked())
        )

        # 저장 및 취소 버튼
        self.save_button = QPushButton("저장")
        self.save_button.clicked.connect(self.accept)

        self.cancel_button = QPushButton("취소")
        self.cancel_button.clicked.connect(self.reject)

        self.layout.addRow("디스크 번호:", self.disc_number)
        self.layout.addRow("트랙 순서:", self.track_order)
        self.layout.addRow("트랙 제목:", self.track_title)
        self.layout.addRow(self.is_title_track)
        self.layout.addRow(self.review_checkbox)
        self.layout.addRow(self.review_text)
        self.layout.addRow(self.save_button, self.cancel_button)

    def get_track_data(self):
        return {
            "disc": self.disc_number.value(),
            "order": self.track_order.value(),
            "title": self.track_title.text(),
            "is_title": self.is_title_track.isChecked(),
            "review": self.review_text.toPlainText() if self.review_checkbox.isChecked() else None,
        }


class AlbumReviewApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Instagram Album Review Creator")
        self.resize(600, 500)

        self.album_info = {}
        self.tracks = []
        self.temp_last_disc = 1
        self.temp_last_order = 1
        self.temp_data_path = "temp.riv"

        # Main layout
        self.main_widget = QWidget()
        self.layout = QVBoxLayout(self.main_widget)

        # temp 데이터 파일 선택해서 불러오기 버튼
        self.load_button = QPushButton("임시 데이터 불러오기")
        self.load_button.clicked.connect(self.load_temp_data)
        self.layout.addWidget(self.load_button)


        # 리뷰 정보
        self.review_number = QSpinBox()
        self.review_number.setMinimum(1)
        self.reviewer_nickname = QLineEdit()
        self.why_review = QTextEdit()

        self.layout.addWidget(QLabel("리뷰 정보"))
        review_form = QFormLayout()
        review_form.addRow("리뷰 번호:", self.review_number)
        review_form.addRow("리뷰어 닉네임:", self.reviewer_nickname)
        review_form.addRow("왜 리뷰를 작성하셨나요?", self.why_review)
        self.layout.addLayout(review_form)

        # Album info
        self.album_name = QLineEdit()
        self.artist_name = QLineEdit()
        self.genre = QLineEdit()
        self.cover_label = QLabel("이미지가 선택되지 않았습니다.")
        self.when = QLineEdit()
        self.playtime = QLineEdit()

        # Event 연결(업데이트)
        self.album_name.textChanged.connect(self.update_album_info)
        self.artist_name.textChanged.connect(self.update_album_info)
        self.genre.textChanged.connect(self.update_album_info)
        self.when.textChanged.connect(self.update_album_info)
        self.review_number.valueChanged.connect(self.update_album_info)
        self.reviewer_nickname.textChanged.connect(self.update_album_info)
        self.why_review.textChanged.connect(self.update_album_info)
        self.playtime.textChanged.connect(self.update_album_info)

        cover_button = QPushButton("커버 이미지 선택")
        cover_button.clicked.connect(self.select_cover_image)

        self.layout.addWidget(QLabel("앨범 정보"))
        album_form = QFormLayout()
        album_form.addRow("앨범 이름:", self.album_name)
        album_form.addRow("아티스트:", self.artist_name)
        album_form.addRow("장르:", self.genre)
        album_form.addRow("발매 연도:", self.when)
        album_form.addRow("재생 시간:", self.playtime)
        album_form.addRow("커버 이미지:", self.cover_label)
        album_form.addRow(cover_button)
        self.layout.addLayout(album_form)

        # Track list
        self.track_list = QListWidget()
        self.track_list.itemSelectionChanged.connect(self.display_track_details)
        self.layout.addWidget(QLabel("트랙들"))
        self.layout.addWidget(self.track_list)

        # Track details
        self.track_details = QLabel("No track selected. Total Tracks: 0, Discs: 0, Total Playtime: 0:00")
        self.layout.addWidget(self.track_details)

        # Add/Delete buttons
        button_layout = QHBoxLayout()
        add_track_button = QPushButton("트랙 추가")
        add_track_button.clicked.connect(self.open_track_dialog)
        self.edit_track_button = QPushButton("트랙 수정")
        self.edit_track_button.setEnabled(False)
        self.edit_track_button.clicked.connect(self.edit_track)
        self.delete_track_button = QPushButton("트랙 삭제")
        self.delete_track_button.setEnabled(False)
        self.delete_track_button.clicked.connect(self.delete_track)
        complete_button = QPushButton("완료")
        self.complete_button = complete_button
        complete_button.clicked.connect(self.complete_album)

        button_layout.addWidget(add_track_button)
        button_layout.addWidget(self.edit_track_button)
        button_layout.addWidget(self.delete_track_button)
        button_layout.addWidget(complete_button)

        self.layout.addLayout(button_layout)
        self.setCentralWidget(self.main_widget)

        self.auto_save_timer = QTimer()
        self.auto_save_timer.timeout.connect(self.save_temp_data)
        self.auto_save_timer.start(30000)

    def update_album_info(self):
        self.album_info["review_number"] = self.review_number.value()
        self.album_info["reviewer_nickname"] = self.reviewer_nickname.text()
        self.album_info["album_name"] = self.album_name.text()
        self.album_info["artist_name"] = self.artist_name.text()
        self.album_info["genre"] = self.genre.text()
        self.album_info["when"] = self.when.text()
        self.album_info['why_review'] = self.why_review.toPlainText()
        self.album_info['playtime'] = self.playtime.text()

    def save_temp_data(self):
        with open(self.temp_data_path, "wb") as f:
            pickle.dump((self.album_info, self.tracks), f)

    def load_temp_data(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Temp Data File", "", "Review Files (*.riv)")
        if file_path:
            self.temp_data_path = file_path
            with open(file_path, "rb") as f:
                temp_album_info, temp_tracks = pickle.load(f)
            self.album_name.setText(temp_album_info.get("album_name", ""))
            self.artist_name.setText(temp_album_info.get("artist_name", ""))
            self.genre.setText(temp_album_info.get("genre", ""))
            self.cover_label.setText(temp_album_info.get("cover_image", ""))
            self.when.setText(temp_album_info.get("when", ""))
            self.review_number.setValue(temp_album_info.get("review_number", 1))
            self.reviewer_nickname.setText(temp_album_info.get("reviewer_nickname", ""))
            self.why_review.setPlainText(temp_album_info.get("why_review", ""))
            self.playtime.setText(temp_album_info.get("playtime", ""))
            self.album_info["cover_image"] = temp_album_info.get("cover_image", "")
            self.tracks = temp_tracks
            self.track_list.clear()
            for track_data in self.tracks:
                self.track_list.addItem(f"Disc {track_data['disc']} - {track_data['order']}: {track_data['title']} {'[Title Track]' if track_data['is_title'] else ''}")
            self.update_track_summary()

    def closeEvent(self, a0):
        self.save_temp_data()
        super().closeEvent(a0)

    def select_cover_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Select Cover Image", "", "Images (*.png *.jpg *.jpeg *.bmp *.webp)")
        if file_path:
            self.cover_label.setText(file_path)
            self.album_info["cover_image"] = file_path

    def open_track_dialog(self):
        dialog = TrackDialog(self.temp_last_disc, self.temp_last_order+1, self)
        if dialog.exec_():
            track_data = dialog.get_track_data()
            self.temp_last_disc = track_data["disc"]
            self.temp_last_order = track_data["order"]
            self.tracks.append(track_data)
            # 디스크와 트랙 순서 기준으로 정렬해서 리스트 업데이트
            self.tracks.sort(key=lambda x: (x["disc"], x["order"]))
            self.track_list.clear()
            for track_data in self.tracks:
                self.track_list.addItem(f"Disc {track_data['disc']} - {track_data['order']}: {track_data['title']} {'[Title Track]' if track_data['is_title'] else ''}")
            # self.track_list.addItem(f"Disc {track_data['disc']} - {track_data['order']}: {track_data['title']}")
            self.update_track_summary()

    def display_track_details(self):
        selected_item = self.track_list.currentItem()
        if selected_item:
            self.delete_track_button.setEnabled(True)
            self.edit_track_button.setEnabled(True)
            index = self.track_list.row(selected_item)
            track = self.tracks[index]
            details = (
                f"Disc: {track['disc']}\n"
                f"Order: {track['order']}\n"
                f"Title: {track['title']}\n"
                f"Title Track: {'Yes' if track['is_title'] else 'No'}\n"
                f"Review: {track['review'] or 'None'}"
            )
            self.track_details.setText(details)
        else:
            self.delete_track_button.setEnabled(False)
            self.edit_track_button.setEnabled(False)
            self.update_track_summary()

    def update_track_summary(self):
        total_tracks = len(self.tracks)
        total_discs = len(set(track["disc"] for track in self.tracks))
        self.track_details.setText(
            f"No track selected. Total Tracks: {total_tracks}, Discs: {total_discs}, Total Playtime: {self.playtime.text()}"
        )

    def delete_track(self):
        selected_item = self.track_list.currentItem()
        if selected_item:
            index = self.track_list.row(selected_item)
            self.track_list.takeItem(index)
            del self.tracks[index]
            self.update_track_summary()

    def edit_track(self):
        selected_item = self.track_list.currentItem()
        if not selected_item:
            return
        index = self.track_list.row(selected_item)
        track = self.tracks[index]

        dialog = TrackDialog(track["disc"], track["order"], self)
        dialog.disc_number.setValue(track["disc"])
        dialog.track_order.setValue(track["order"])
        dialog.track_title.setText(track["title"])
        dialog.is_title_track.setChecked(track["is_title"])
        if track["review"]:
            dialog.review_checkbox.setChecked(True)
            dialog.review_text.setPlainText(track["review"])

        if dialog.exec_():
            updated_track_data = dialog.get_track_data()
            self.tracks[index] = updated_track_data
            self.tracks.sort(key=lambda x: (x["disc"], x["order"]))
            self.track_list.clear()
            for track_data in self.tracks:
                self.track_list.addItem(f"Disc {track_data['disc']} - {track_data['order']}: {track_data['title']} {'[Title Track]' if track_data['is_title'] else ''}")
            self.update_track_summary()

    def complete_album(self):
        # 빈 칸 체크
        if not all(self.album_info.values()):
            return
        if not self.tracks:
            return
        if not all([self.review_number.value(), self.artist_name.text(), self.album_name.text(), self.reviewer_nickname.text()]):
            return
        save_folder = QFileDialog.getExistingDirectory(self, "Select Save Folder")
        if not save_folder:
            return
        invalid_chars = ['\\', '/', ':', '*', '?', '"', '<', '>', '|']
        save_folder = os.path.join(save_folder, f"{''.join([char for char in self.album_name.text() if char not in invalid_chars])}")
        os.makedirs(save_folder, exist_ok=True)
        self.complete_button.setEnabled(False)
        self.complete_button.setText("이미지 제작 중...")
        title_page(save_folder, self.review_number.value(), self.artist_name.text(), self.album_name.text(), self.reviewer_nickname.text())
        mood_page(save_folder, self.review_number.value(), self.album_info["cover_image"], self.album_name.text(), self.artist_name.text(), len(self.tracks), f"{self.playtime.text()}", self.when.text(), self.genre.text(), self.why_review.toPlainText())
        list_page(save_folder, self.review_number.value(), self.tracks)
        review_page(save_folder, self.review_number.value(), self.tracks)
        self.complete_button.setEnabled(True)
        self.complete_button.setText("완료")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AlbumReviewApp()
    window.show()
    sys.exit(app.exec_())