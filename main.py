import sys
import dataclasses
import random

from PySide6.QtWidgets import QApplication, QMainWindow, QPushButton

import ui_main_window


CARDS_COUNT = 5

EMPTY = 0
HAS_WORD = 1
CHOOSEN = 2

state_to_color = [
  "777777",
  "777777",
  "222277",
]

buttons = {
  "left": [],
  "right": [],
}

russian_words = [
  "Забронировать",
  "отель",
  "купить",
  "билеты",
  "на",
  "конференцию",
]

english_words = [
  "Book",
  "hotel",
  "buy",
  "tickets",
  "for",
  "conference",
]

collection = list(zip(russian_words, english_words))

active_words = []
words_state = {
  "left": [EMPTY] * CARDS_COUNT,
  "right": [EMPTY] * CARDS_COUNT,
}
words_to_fill = CARDS_COUNT
score = 0


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
    buttons["left"][word.left_offset].setText(collection[word.index][0])
    buttons["right"][word.right_offset].setText(collection[word.index][1])


@dataclasses.dataclass
class ActiveWord:
  index: int
  left_offset: int
  right_offset: int

active_button = None

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


class App(QMainWindow):
  def __init__(self):
    super(App, self).__init__()
    self.ui = ui_main_window.Ui_MainWindow()
    self.ui.setupUi(self)
    for index in range(CARDS_COUNT):
      button = QPushButton()
      button.setFixedHeight(100)
      buttons["left"].append(button)
      self.ui.LeftSide.addWidget(button)
      button.clicked.connect(on_button_click("left", index))
      button = QPushButton()
      button.setFixedHeight(100)
      buttons["right"].append(button)
      self.ui.RightSide.addWidget(button)
      button.clicked.connect(on_button_click("right", index))

    fill_cards()


if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = App()
  window.show()

  sys.exit(app.exec())
