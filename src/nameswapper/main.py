import shutil
from pathlib import Path

from PySide6 import QtCore, QtWidgets


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        self.setMinimumWidth(960)
        self.setMinimumHeight(350)
        self.setWindowTitle("NameSwapper")
        self.grid = QtWidgets.QGridLayout()
        self.container = QtWidgets.QWidget()
        self.container.setLayout(self.grid)
        self.setCentralWidget(self.container)
        self.input_file: Path = Path()

        self.shared_scrollbar = QtWidgets.QScrollBar(QtCore.Qt.Orientation.Vertical)
        self.shared_scrollbar.setMinimum(1)
        self.shared_scrollbar.setMaximum(2)
        # self.shared_scrollbar.setStyleSheet("QScrollBar { background-color: red; }")

        self.label_input_file = QtWidgets.QLabel("Input File:")
        self.label_input_names = QtWidgets.QLabel("Names")
        self.label_output_names = QtWidgets.QLabel(
            "Output File Names\n(Saved in the same location as the input file)",
            alignment=QtCore.Qt.AlignmentFlag.AlignTop,
        )
        self.list_output_names = QtWidgets.QListWidget(sortingEnabled=False)
        self.list_output_names.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.NoSelection)

        self.status_label = QtWidgets.QLabel(text="")

        self.button_select_input_file = QtWidgets.QPushButton("Select Input File")
        self.button_select_input_file.clicked.connect(self.get_file)
        self.button_select_input_file.clicked.connect(self.check_requirements)

        self.button_execute = QtWidgets.QPushButton("Select a file and enter names")
        self.button_execute.setEnabled(False)
        self.button_execute.setStyleSheet("padding-left: 10px; padding-right: 10px; padding-top: 15px; padding-bottom: 15px")
        self.button_execute.clicked.connect(self.copy_files)

        self.input_text_box = QtWidgets.QPlainTextEdit(placeholderText="Paste a list of names here...")
        self.input_text_box.textChanged.connect(self.check_requirements)
        self.input_text_box.textChanged.connect(self.sync_scrolling_widget_location)

        self.grid.addWidget(self.label_input_file, 0, 0, alignment=QtCore.Qt.AlignmentFlag.AlignLeft)
        self.grid.addWidget(self.label_input_names, 1, 0, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(self.label_output_names, 1, 2, alignment=QtCore.Qt.AlignmentFlag.AlignTop)
        self.grid.addWidget(self.button_select_input_file, 0, 2)
        self.grid.addWidget(self.shared_scrollbar, 2, 1)
        self.grid.addWidget(self.input_text_box, 2, 0)
        self.grid.addWidget(self.button_execute, 3, 0, 2, 3, alignment=QtCore.Qt.AlignmentFlag.AlignCenter)
        self.grid.addWidget(self.status_label, 4, 0, 2, 3)
        self.grid.addWidget(self.list_output_names, 2, 2)

        # connect scrollbars
        self.input_text_box.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.list_output_names.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.input_text_box.verticalScrollBar().valueChanged.connect(self.sync_scrolling_widget_location)
        self.list_output_names.verticalScrollBar().valueChanged.connect(self.sync_scrolling_widget_location)
        self.shared_scrollbar.valueChanged.connect(self.sync_scrolling_widget_location)

    def sync_scrollbars(self):
        self.shared_scrollbar.blockSignals(True)
        source_scrollbar = self.input_text_box.verticalScrollBar()
        self.shared_scrollbar.setMinimum(source_scrollbar.minimum())
        self.shared_scrollbar.setMaximum(source_scrollbar.maximum())
        self.shared_scrollbar.setPageStep(source_scrollbar.pageStep())
        self.shared_scrollbar.setValue(source_scrollbar.value())
        self.shared_scrollbar.blockSignals(False)

    def sync_scrolling_widget_location(self, value):
        text_scrollbar = self.input_text_box.verticalScrollBar()
        list_scrollbar = self.list_output_names.verticalScrollBar()

        ratio = 0
        if text_scrollbar.maximum() > 0:
            ratio = value / text_scrollbar.maximum()
        list_value = int(ratio * list_scrollbar.maximum())

        self.input_text_box.verticalScrollBar().setValue(value)
        self.list_output_names.verticalScrollBar().setValue(list_value)
        self.shared_scrollbar.setValue(value)
        # self.sync_scrollbars()

    def input_names(self) -> list[str]:
        return self.input_text_box.toPlainText().split("\n")

    def get_file(self):
        file, _ = QtWidgets.QFileDialog.getOpenFileName()
        self.input_file = Path(file)
        self.label_input_file.setText(f"Input File: {self.input_file}")

    def check_requirements(self):
        content = [f"{self.input_file.stem} {name}{self.input_file.suffix}" for name in self.input_names()]
        self.sync_scrollbars()

        if self.input_text_box.toPlainText() == "":
            self.list_output_names.clear()
        elif self.input_file.as_posix() != "." and self.input_text_box.toPlainText() != "":
            self.button_execute.setEnabled(True)
            self.button_execute.setText("Create files!")
            self.list_output_names.clear()
            self.list_output_names.addItems(content)

    def copy_files(self):
        root_output_dir = self.input_file.parent
        # Get contents of list
        for i in range(self.list_output_names.count()):
            destination_filepath = Path(self.input_file.parent, self.list_output_names.item(i).text())
            # copy the file
            shutil.copy2(self.input_file, destination_filepath)
        self.status_label.setText(f"Finished creating {self.list_output_names.count()} file(s)!")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
