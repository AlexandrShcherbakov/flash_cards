import pathlib
import os
import sys
import dataclasses
import random
import json

from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton

import ui_create_list
import ui_main_window
import ui_open_list
import ui_add_word


CARDS_COUNT = 5

EMPTY = 0
HAS_WORD = 1
CHOOSEN = 2

LISTS_FILTER = "./lists"

state_to_color = [
  "777777",
  "777777",
  "222277",
]

buttons = {
  "left": [],
  "right": [],
}

collection = []

active_words = []
words_state = {
  "left": [EMPTY] * CARDS_COUNT,
  "right": [EMPTY] * CARDS_COUNT,
}
words_to_fill = CARDS_COUNT
score = 0
active_list_name = None
active_button = None


def fill_cards():
  empty_left = []
  empty_right = []
  for idx in range(CARDS_COUNT):
    if words_state["left"][idx] == EMPTY:
      empty_left.append(idx)
      words_state["left"][idx] = HAS_WORD
    if words_state["right"][idx] == EMPTY:
      empty_right.append(idx)
      words_state["right"][idx] = HAS_WORD
  random.shuffle(empty_right)
  empty_pairs = list(zip(empty_left, empty_right))
  random.shuffle(empty_pairs)
  for left_idx, right_idx in empty_pairs:
    idx = random.randint(0, len(collection) - 1)
    while any(idx == x.index for x in active_words):
      idx = random.randint(0, len(collection) - 1)
    active_words.append(ActiveWord(idx, left_idx, right_idx))
  global words_to_fill
  words_to_fill = 0
  render_buttons()


def render_buttons():
  for side in ["left", "right"]:
    for button, state in zip(buttons[side], words_state[side]):
      button.setText("")
      button.setStyleSheet(f'QPushButton {{background-color: #{state_to_color[state]}; font: 24px;}}')
  for word in active_words:
    buttons["left"][word.left_offset].setText(collection[word.index]["words"][0])
    buttons["right"][word.right_offset].setText(collection[word.index]["words"][1])


@dataclasses.dataclass
class ActiveWord:
  index: int
  left_offset: int
  right_offset: int


def get_active_list_file():
  global active_list_name
  return pathlib.Path(LISTS_FILTER) / (active_list_name + ".json")


def dump_list():
  with get_active_list_file().open("w") as fin:
    fin.write(json.dumps(collection))


def on_button_click(label, idx):
  def process_click():
    try:
      global active_button
      current_idx = None
      current_idx = (label, idx)
      same_column = active_button and active_button[0] == label
      if same_column:
        words_state[label][active_button[1]] = HAS_WORD
      if active_button == None or same_column:
        active_button = current_idx
        words_state[label][idx] = CHOOSEN
        return

      left_idx = idx if label == "left" else active_button[1]
      right_idx = idx if label == "right" else active_button[1]

      for word_idx, word in enumerate(active_words):
        if word.left_offset != left_idx:
          continue
        if word.right_offset != right_idx:
          words_state[active_button[0]][active_button[1]] = HAS_WORD
          active_button = None
          return
        active_button = None
        words_state["left"][left_idx] = EMPTY
        words_state["right"][right_idx] = EMPTY
        global score, words_to_fill
        score += 1
        words_to_fill += 1
        if words_to_fill >= random.randint(2, 3):
          fill_cards()
        del active_words[word_idx]
        break
    finally:
      render_buttons()
  return process_click


class CreateListDialog(QDialog):
  def __init__(self, main_window):
    super(CreateListDialog, self).__init__()
    self.ui = ui_create_list.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(lambda : self.try_to_create_list())
    self.main_window = main_window
    self.main_window.setStatusTip("")

  def try_to_create_list(self):
    folderPath = pathlib.Path(LISTS_FILTER)
    folderPath.mkdir(exist_ok=True)
    list_name = self.ui.listName.text()
    list_path = folderPath / (list_name + ".json")
    if list_path.exists():
      self.main_window.setStatusTip(f"Список {list_name} уже существует.")
    else:
      list_path.touch()
      self.main_window.setStatusTip(f"Список {list_name} создан.")
      global active_list_name
      active_list_name = list_name
    update_menu_state(self.main_window)


class OpenListDialog(QDialog):
  def __init__(self, main_window):
    super(OpenListDialog, self).__init__()
    self.ui = ui_open_list.Ui_Dialog()
    self.ui.setupUi(self)
    self.ui.ListOfLists.addItems(x.rsplit(".")[0] for x in os.listdir(LISTS_FILTER) if x.endswith("json"))
    self.accepted.connect(lambda : self.open_list())
    self.main_window = main_window
    self.main_window.setStatusTip("")

  def open_list(self):
    list_name = self.ui.ListOfLists.currentText()
    global active_list_name
    active_list_name = list_name
    self.main_window.setStatusTip(f"Выбран список {list_name}.")
    update_menu_state(self.main_window)


class AddWordDialog(QDialog):
  def __init__(self, main_window):
    super(AddWordDialog, self).__init__()
    self.ui = ui_add_word.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(lambda : self.add_word())
    self.main_window = main_window
    self.main_window.setStatusTip("")

  def add_word(self):
    word1 = self.ui.word1.text()
    word2 = self.ui.word2.text()
    collection.append({"words": (word1, word2), "score": 0})
    dump_list()
    global active_list_name
    self.main_window.setStatusTip(f"Слово/фраза {word1} теперь есть в списке {active_list_name}.")


def has_lists():
  return pathlib.Path(LISTS_FILTER).exists() and any(x.endswith("json") for x in os.listdir(LISTS_FILTER))


def can_add_word():
  return has_lists() and active_list_name != None


def update_menu_state(main_window):
  main_window.ui.open_list.setVisible(has_lists())
  main_window.ui.add_word.setVisible(can_add_word())


class App(QMainWindow):
  def __init__(self):
    super(App, self).__init__()
    self.ui = ui_main_window.Ui_MainWindow()
    self.ui.setupUi(self)
    self.ui.createList.triggered.connect(lambda : CreateListDialog(self).exec())
    self.ui.open_list.triggered.connect(lambda : OpenListDialog(self).exec())
    self.ui.add_word.triggered.connect(lambda : AddWordDialog(self).exec())
    for index in range(CARDS_COUNT):
      for side in ["left", "right"]:
        button = QPushButton()
        button.setFixedHeight(100)
        buttons[side].append(button)
        getattr(self.ui, side + "_side").addWidget(button)
        button.clicked.connect(on_button_click(side, index))

    update_menu_state(self)


if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = App()
  window.show()

  sys.exit(app.exec())
