import pathlib
import os
import sys
import dataclasses
import random
import json
import datetime

from PySide6.QtWidgets import (
  QApplication,
  QDialog,
  QMainWindow,
  QPushButton,
  QLineEdit,
  QLabel,
  QDialogButtonBox,
  QFileDialog,
)

import ui_main_window
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

state_to_color = [
  "BFB5B9",
  "BFB5B9",
  "FFBE9E",
]

buttons = {
  "left": [],
  "right": [],
}


class Context:
  def __init__(self):
    self.active_words = []
    self.words_state = {
      "left": [EMPTY] * CARDS_COUNT,
      "right": [EMPTY] * CARDS_COUNT,
    }
    self.collection = []
    self.score = 0
    self.errors = 0
    self.active_list_path = None
    self.active_button = None
    self.train_start = None

  def reset(self):
    self.active_words = []
    self.words_state = {
      "left": [EMPTY] * CARDS_COUNT,
      "right": [EMPTY] * CARDS_COUNT,
    }
    self.score = 0
    self.errors = 0
    self.active_button = None
    self.train_start = None

  def is_word_active(self, idx):
    return any(idx == x.index for x in self.active_words)

  def is_trained_word(self, idx):
    return self.collection[idx]["score"] >= REPETITIONS_TO_TRAIN

  def activate_word(self, left_idx, right_idx):
    self.active_words.append(ActiveWord(select_word(), left_idx, right_idx))

  @property
  def words_to_fill(self):
    return CARDS_COUNT - len(self.active_words)

  @property
  def active_list_name(self):
    return self.active_list_path.name.rsplit(".", maxsplit=1)[0]

  @property
  def has_list(self):
    return self.active_list_path is not None

  def dump_list(self):
    with self.active_list_path.open("w") as fout:
      fout.write(json.dumps(self.collection))

  def load_list(self):
    with self.active_list_path.open("r") as fin:
      self.collection = json.loads(fin.read())


CONTEXT = Context()


def select_word():
  words = [
    idx for idx in range(len(CONTEXT.collection))
    if not CONTEXT.is_trained_word(idx) and not CONTEXT.is_word_active(idx)
  ][:POOL_SIZE]
  words += [
    idx for idx in range(len(CONTEXT.collection))
    if CONTEXT.is_trained_word(idx) and not CONTEXT.is_word_active(idx)
  ]
  weights = [
    1 if not CONTEXT.is_trained_word(idx) else
      0.5 * (0.95 ** (CONTEXT.collection[idx]["score"] / REPETITIONS_TO_TRAIN))
    for idx in words
  ]
  return random.choices(words, weights)[0]


def fill_cards():
  empty_left = []
  empty_right = []
  for idx in range(CARDS_COUNT):
    if CONTEXT.words_state["left"][idx] == EMPTY:
      empty_left.append(idx)
      CONTEXT.words_state["left"][idx] = HAS_WORD
    if CONTEXT.words_state["right"][idx] == EMPTY:
      empty_right.append(idx)
      CONTEXT.words_state["right"][idx] = HAS_WORD
  random.shuffle(empty_right)
  for left_idx, right_idx in zip(empty_left, empty_right):
    CONTEXT.activate_word(left_idx, right_idx)
  render_buttons()


def render_buttons():
  for side in ["left", "right"]:
    for button, state in zip(buttons[side], CONTEXT.words_state[side]):
      button.setText("")
      button.setStyleSheet(
        f'QPushButton {{background-color: #{state_to_color[state]}; font: 24px;}}'
      )
  for word in CONTEXT.active_words:
    buttons["left"][word.left_offset].setText(CONTEXT.collection[word.index]["words"][0])
    buttons["right"][word.right_offset].setText(CONTEXT.collection[word.index]["words"][1])


@dataclasses.dataclass
class ActiveWord:
  index: int
  left_offset: int
  right_offset: int


def on_button_click(label, idx):
  def process_click():
    try:
      if CONTEXT.words_state[label][idx] == EMPTY:
        return
      current_idx = None
      current_idx = (label, idx)
      if CONTEXT.active_button == current_idx:
        CONTEXT.words_state[label][idx] = HAS_WORD
        CONTEXT.active_button = None
        return
      same_column = CONTEXT.active_button and CONTEXT.active_button[0] == label
      if same_column:
        CONTEXT.words_state[label][CONTEXT.active_button[1]] = HAS_WORD
      if CONTEXT.active_button is None or same_column:
        CONTEXT.active_button = current_idx
        CONTEXT.words_state[label][idx] = CHOOSEN
        return

      left_idx = idx if label == "left" else CONTEXT.active_button[1]
      right_idx = idx if label == "right" else CONTEXT.active_button[1]

      for word_idx, word in enumerate(CONTEXT.active_words):
        if word.left_offset != left_idx:
          continue
        if word.right_offset != right_idx:
          CONTEXT.words_state[CONTEXT.active_button[0]][CONTEXT.active_button[1]] = HAS_WORD
          CONTEXT.active_button = None
          CONTEXT.collection[CONTEXT.active_words[word_idx].index]["score"] -= 1
          CONTEXT.errors += 1
          return
        CONTEXT.active_button = None
        CONTEXT.words_state["left"][left_idx] = EMPTY
        CONTEXT.words_state["right"][right_idx] = EMPTY
        CONTEXT.score += 1
        CONTEXT.collection[CONTEXT.active_words[word_idx].index]["score"] += 1
        if CONTEXT.score == TRAIN_LENGTH:
          FinishTrainDialog().exec()
          return
        CONTEXT.active_words = CONTEXT.active_words[:word_idx] + CONTEXT.active_words[word_idx + 1:]
        if CONTEXT.words_to_fill >= random.randint(2, 3):
          fill_cards()
        break
    finally:
      render_buttons()
  return process_click


class AddWordDialog(QDialog):
  def __init__(self, main_window):
    super(AddWordDialog, self).__init__()
    self.ui = ui_add_word.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(self.add_word)
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.ui.word1.textChanged.connect(self.update_accept_button_state)
    self.ui.word2.textChanged.connect(self.update_accept_button_state)
    self.update_accept_button_state()

  def update_accept_button_state(self):
    acceptable = (
      self.ui.word1.text() != ""
      and self.ui.word2.text() != ""
      and not any(self.ui.word1.text() in x["words"] for x in CONTEXT.collection)
      and not any(self.ui.word2.text() in x["words"] for x in CONTEXT.collection)
    )
    self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Ok).setEnabled(acceptable)

  def add_word(self):
    word1 = self.ui.word1.text()
    word2 = self.ui.word2.text()
    CONTEXT.collection.append({"words": (word1, word2), "score": 0})
    CONTEXT.dump_list()
    self.main_window.setStatusTip(
      f"Слово/фраза {word1} теперь есть в списке {CONTEXT.active_list_name}."
    )
    update_menu_state(self.main_window)


class ChangeListDialog(QDialog):
  def __init__(self, main_window):
    super(ChangeListDialog, self).__init__()
    self.ui = ui_edit_words_list.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(self.save_list)
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.removed_words = []
    self.rerender()

  def save_list(self):
    self.main_window.setStatusTip(f"Список {CONTEXT.active_list_name} сохранён.")
    new_collection = []
    row = 0
    for index, word in enumerate(CONTEXT.collection):
      if index in self.removed_words:
        continue
      new_collection.append(word)
      for i in range(2):
        new_collection[-1]["words"][i] = (
          self.ui.words_list.itemAtPosition(row, i + 1).widget().text()
        )
      row += 1
    CONTEXT.collection = new_collection
    CONTEXT.dump_list()
    reset_stats()
    update_menu_state(self.main_window)
    render_buttons()

  def rerender(self):
    self.ui.label.setText(
      f"Список {CONTEXT.active_list_name} содержит "
      + f"{len(CONTEXT.collection) - len(self.removed_words)} слов"
    )
    for i in reversed(range(self.ui.words_list.count())):
      self.ui.words_list.itemAt(i).widget().deleteLater()
    row = 0
    for index, word in enumerate(CONTEXT.collection):
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
    self.finished.connect(self.finish_train)
    self.ui.correct_words_count.setText(str(CONTEXT.score))
    self.ui.errors_count.setText(str(CONTEXT.errors))
    self.ui.correctness_percentage.setText(
      str(round(CONTEXT.score / (CONTEXT.score + CONTEXT.errors) * 100, 2))
    )
    self.ui.train_time.setText(
      str(datetime.datetime.now() - CONTEXT.train_start).split(".", maxsplit=1)[0]
    )
    self.ui.learned_count.setText(
      str(len([x for x in range(len(CONTEXT.collection)) if CONTEXT.is_trained_word(x)]))
    )

  def finish_train(self):
    CONTEXT.dump_list()
    reset_stats()
    render_buttons()


def can_modify_list():
  return CONTEXT.has_list


def can_start_train():
  return (CONTEXT.has_list and len(CONTEXT.collection) >= CARDS_COUNT)


def update_menu_state(main_window):
  main_window.ui.add_word.setVisible(can_modify_list())
  main_window.ui.start_train.setVisible(can_start_train())
  main_window.ui.change_list.setVisible(can_modify_list())


def reset_stats():
  CONTEXT.reset()


def start_train():
  reset_stats()
  fill_cards()
  CONTEXT.train_start = datetime.datetime.now()


class App(QMainWindow):
  def __init__(self):
    super(App, self).__init__()
    self.ui = ui_main_window.Ui_MainWindow()
    self.ui.setupUi(self)
    self.ui.createList.triggered.connect(self.create_list)
    self.ui.open_list.triggered.connect(self.open_list)
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

  def create_list(self):
    self.setToolTip("")
    dialog = QFileDialog()
    dialog.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
    dialog.setNameFilter("JSON files (*.json)")
    if dialog.exec():
      list_path = pathlib.Path(dialog.selectedFiles()[0])
      try:
        if list_path.exists():
          self.setStatusTip(f"Список {list_path} уже существует.")
          return
        CONTEXT.active_list_path = list_path
        CONTEXT.dump_list()
        self.setStatusTip(f"Список {CONTEXT.active_list_name} создан.")
      finally:
        update_menu_state(self)

  def open_list(self):
    self.setToolTip("")
    dialog = QFileDialog()
    dialog.setFileMode(QFileDialog.ExistingFile)
    dialog.setNameFilter("JSON files (*.json)")
    if dialog.exec():
      CONTEXT.active_list_path = pathlib.Path(dialog.selectedFiles()[0])
      self.setToolTip(f"Выбран список {CONTEXT.active_list_name}.")
      CONTEXT.load_list()
      update_menu_state(self)


if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = App()
  window.show()

  sys.exit(app.exec())
