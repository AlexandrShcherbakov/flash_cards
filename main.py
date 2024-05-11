import pathlib
import os
import sys
import dataclasses
import random
import json
import datetime

from PySide6.QtWidgets import QApplication, QDialog, QMainWindow, QPushButton, QLineEdit, QLabel

import ui_create_list
import ui_main_window
import ui_open_list
import ui_add_word
import ui_train_finish
import ui_edit_words_list


CARDS_COUNT = 5
TRAIN_LENGTH = 50
REPETITIONS_TO_TRAIN = 20
POOL_SIZE = 25

EMPTY = 0
HAS_WORD = 1
CHOOSEN = 2

LISTS_FOLDER = "./lists"

state_to_color = [
  "BFB5B9",
  "BFB5B9",
  "FFBE9E",
]

buttons = {
  "left": [],
  "right": [],
}

collection = []

active_words = None
words_state = None
words_to_fill = None
score = None
errors = None
active_list_name = None
active_button = None
train_start = None


def trained_word(idx):
  return collection[idx]["score"] >= REPETITIONS_TO_TRAIN


def is_word_active(idx):
  return any(idx == x.index for x in active_words)


def select_word():
  words = [idx for idx in range(len(collection)) if not trained_word(idx) and not is_word_active(idx)][:POOL_SIZE]
  words += [idx for idx in range(len(collection)) if trained_word(idx) and not is_word_active(idx)]
  weights = [1 if not trained_word(idx) else 0.5 * (0.95 ** (collection[idx]["score"] / REPETITIONS_TO_TRAIN)) for idx in words]
  return random.choices(words, weights)[0]


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
  for left_idx, right_idx in zip(empty_left, empty_right):
    active_words.append(ActiveWord(select_word(), left_idx, right_idx))
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
  return pathlib.Path(LISTS_FOLDER) / (active_list_name + ".json")


def dump_list():
  with get_active_list_file().open("w") as fout:
    fout.write(json.dumps(collection))


def load_list():
  with get_active_list_file().open("r") as fin:
    global collection
    collection = json.loads(fin.read())


def on_button_click(label, idx):
  def process_click():
    try:
      global active_button, active_words, errors
      if words_state[label][idx] == EMPTY:
        return
      current_idx = None
      current_idx = (label, idx)
      if active_button == current_idx:
        words_state[label][idx] = HAS_WORD
        active_button = None
        return
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
          collection[active_words[word_idx].index]["score"] -= 1
          errors += 1
          return
        active_button = None
        words_state["left"][left_idx] = EMPTY
        words_state["right"][right_idx] = EMPTY
        global score, words_to_fill
        score += 1
        collection[active_words[word_idx].index]["score"] += 1
        if score == TRAIN_LENGTH:
          FinishTrainDialog().exec()
          return
        active_words = active_words[:word_idx] + active_words[word_idx + 1:]
        words_to_fill += 1
        if words_to_fill >= random.randint(2, 3):
          fill_cards()
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
    folderPath = pathlib.Path(LISTS_FOLDER)
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
    self.ui.ListOfLists.addItems(x.rsplit(".")[0] for x in os.listdir(LISTS_FOLDER) if x.endswith("json"))
    self.accepted.connect(lambda : self.open_list())
    self.main_window = main_window
    self.main_window.setStatusTip("")

  def open_list(self):
    list_name = self.ui.ListOfLists.currentText()
    global active_list_name
    active_list_name = list_name
    self.main_window.setStatusTip(f"Выбран список {list_name}.")
    load_list()
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
    update_menu_state(self.main_window)


class ChangeListDialog(QDialog):
  def __init__(self, main_window):
    super(ChangeListDialog, self).__init__()
    self.ui = ui_edit_words_list.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(lambda : self.save_list())
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.removed_words = []
    self.rerender()

  def save_list(self):
    global active_list_name, collection
    self.main_window.setStatusTip(f"Список {active_list_name} сохранён.")
    new_collection = []
    row = 0
    for index, word in enumerate(collection):
      if index in self.removed_words:
        continue
      new_collection.append(word)
      for i in range(2):
        new_collection[-1]["words"][i] = self.ui.words_list.itemAtPosition(row, i + 1).widget().text()
      row += 1
    collection = new_collection
    dump_list()
    reset_stats()
    update_menu_state(self.main_window)
    render_buttons()

  def rerender(self):
    self.ui.label.setText(f"Список {active_list_name} содержит {len(collection) - len(self.removed_words)} слов")
    for i in reversed(range(self.ui.words_list.count())):
      self.ui.words_list.itemAt(i).widget().deleteLater()
    row = 0
    for index, word in enumerate(collection):
      if index in self.removed_words:
        continue
      self.ui.words_list.addWidget(QLabel(str(row)), row, 0)
      for i in range(2):
        word_edit = QLineEdit()
        word_edit.setText(word["words"][i])
        self.ui.words_list.addWidget(word_edit, row, i + 1)
      self.ui.words_list.addWidget(QLabel(str(word["score"])), row, 3)
      remove_button = QPushButton("Удалить")
      def gen_remove_callback(dialog, index):
        def remove_item():
          dialog.removed_words.append(index)
          dialog.rerender()
        return remove_item
      remove_button.clicked.connect(gen_remove_callback(self, index))
      self.ui.words_list.addWidget(remove_button, row, 4)
      row += 1


class FinishTrainDialog(QDialog):
  def __init__(self):
    super(FinishTrainDialog, self).__init__()
    self.ui = ui_train_finish.Ui_Dialog()
    self.ui.setupUi(self)
    self.finished.connect(lambda : self.finish_train())
    self.ui.correct_words_count.setText(str(score))
    self.ui.errors_count.setText(str(errors))
    self.ui.correctness_percentage.setText(str(round(score / (score + errors) * 100, 2)))
    self.ui.train_time.setText(str(datetime.datetime.now() - train_start).split(".")[0])
    self.ui.learned_count.setText(str(len([x for x in range(len(collection)) if trained_word(x)])))

  def finish_train(self):
    dump_list()
    reset_stats()
    render_buttons()


def has_lists():
  return pathlib.Path(LISTS_FOLDER).exists() and any(x.endswith("json") for x in os.listdir(LISTS_FOLDER))


def can_modify_list():
  return has_lists() and active_list_name != None


def can_start_train():
  return has_lists() and active_list_name != None and len(collection) >= CARDS_COUNT


def update_menu_state(main_window):
  main_window.ui.open_list.setVisible(has_lists())
  main_window.ui.add_word.setVisible(can_modify_list())
  main_window.ui.start_train.setVisible(can_start_train())
  main_window.ui.change_list.setVisible(can_modify_list())


def reset_stats():
  global active_words, words_state, words_to_fill, score, errors
  active_words = []
  words_state = {
    "left": [EMPTY] * CARDS_COUNT,
    "right": [EMPTY] * CARDS_COUNT,
  }
  words_to_fill = CARDS_COUNT
  score = 0
  errors = 0


def start_train():
  reset_stats()
  fill_cards()
  global train_start
  train_start = datetime.datetime.now()


class App(QMainWindow):
  def __init__(self):
    super(App, self).__init__()
    self.ui = ui_main_window.Ui_MainWindow()
    self.ui.setupUi(self)
    self.ui.createList.triggered.connect(lambda : CreateListDialog(self).exec())
    self.ui.open_list.triggered.connect(lambda : OpenListDialog(self).exec())
    self.ui.add_word.triggered.connect(lambda : AddWordDialog(self).exec())
    self.ui.change_list.triggered.connect(lambda : ChangeListDialog(self).exec())
    self.ui.start_train.triggered.connect(start_train)
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
