import pathlib
import sys
import dataclasses
import random
import json
import datetime
import unicodedata
import re
import os
import concurrent.futures

from paramiko import SSHClient
from scp import SCPClient

from PySide6.QtWidgets import (
  QApplication,
  QDialog,
  QMainWindow,
  QPushButton,
  QLineEdit,
  QLabel,
  QDialogButtonBox,
  QFileDialog,
  QFormLayout,
  QVBoxLayout,
  QSpinBox,
  QWidget,
)

import ui_main_window
import ui_add_word
import ui_train_finish
import ui_edit_words_list
import ui_spelling_task
import ui_settings
import ui_net_settings


CARDS_COUNT = 5

LOCALIZATION = {
  "train_length": "Количество слов для тренировки",
  "repetitions_to_train": "Количество повторений для выучивания",
  "active_pool_size": "Количество активно изучаемых новых слов",
  "cards": "Упржнение с карточками",
  "spelling": "Упражнение с написанием перевода",
}

@dataclasses.dataclass
class ExcerciseSettings:
  train_length : int = 50
  repetitions_to_train : int = 20
  active_pool_size : int = 25


@dataclasses.dataclass
class Settings:
  cards : ExcerciseSettings = ExcerciseSettings()
  spelling : ExcerciseSettings = ExcerciseSettings(20, 20, 10)

@dataclasses.dataclass
class NetSettings:
  ip : str = ""
  user : str = ""


REMOTE_FOLDER_NAME = "flash_cards"
SETTINGS_FILENAME = "settings.json"
NETWORK_SETTINGS_FILENAME = "network.json"

def load_settings():
  settings = Settings()
  local_sync_file(SETTINGS_FILENAME)
  if os.path.exists(SETTINGS_FILENAME):
    with open(SETTINGS_FILENAME, "r", encoding="utf-8") as fin:
      settings_json = json.loads(fin.read())
      for excersize, ex_settings in settings_json.items():
        setattr(settings, excersize, ExcerciseSettings(**ex_settings))
  return settings


def save_settings():
  with open(SETTINGS_FILENAME, "w", encoding="utf-8") as fout:
    fout.write(json.dumps(dataclasses.asdict(SETTINGS)))
  remote_sync_file(SETTINGS_FILENAME)


def load_net_settings():
  settings = NetSettings()
  if os.path.exists(NETWORK_SETTINGS_FILENAME):
    with open(NETWORK_SETTINGS_FILENAME, "r", encoding="utf-8") as fin:
      settings = NetSettings(**json.loads(fin.read()))
      ssh.load_system_host_keys()
      ssh.connect(settings.ip, username=settings.user)
  return settings


def save_net_settings():
  ssh.load_system_host_keys()
  ssh.connect(NET_SETTINGS.ip, username=NET_SETTINGS.user)
  with open(NETWORK_SETTINGS_FILENAME, "w", encoding="utf-8") as fout:
    fout.write(json.dumps(dataclasses.asdict(NET_SETTINGS)))


def local_sync_file(filepath):
  if not NET_SETTINGS.ip:
    return
  with SCPClient(ssh.get_transport()) as scp:
    remote_path = f"{REMOTE_FOLDER_NAME}/{pathlib.Path(filepath).as_posix()}"
    remote_ts = ssh.exec_command(f"stat -c %Y {remote_path}")[1].read().decode()
    if remote_ts:
      remote_time = int(remote_ts)
      local_time = int(os.path.getmtime(filepath) if os.path.exists(filepath) else 0)
      if remote_time >= local_time:
        scp.get(remote_path, filepath, preserve_times=True)


def remote_sync_file(filepath):
  if not NET_SETTINGS.ip:
    return
  def impl(filepath):
    with SCPClient(ssh.get_transport()) as scp:
      local_path = pathlib.Path(filepath)
      remote_subpath = local_path.as_posix()
      remote_path = f"{REMOTE_FOLDER_NAME}/{remote_subpath}"
      if os.path.exists(filepath):
        ssh.exec_command(f"mkdir -p {REMOTE_FOLDER_NAME}/{local_path.parent.as_posix()}")
        scp.put(filepath, remote_path, preserve_times=True)
  return executor.submit(impl, filepath)


ssh = SSHClient()
executor = concurrent.futures.ThreadPoolExecutor()
NET_SETTINGS = load_net_settings()
SETTINGS = load_settings()

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

greek_pattern = re.compile(r'[\u0370-\u03FF\u1F00-\u1FFF]')
english_pattern = re.compile(r'[a-zA-Z]')

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
    return self.collection[idx]["score"] >= SETTINGS.cards.repetitions_to_train

  def is_spelling_trained_word(self, idx):
    return self.collection[idx].get("spelling_score", 0) >= SETTINGS.spelling.repetitions_to_train

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

  def auto_correction(self):
    for record in self.collection:
      word1, word2 = record["words"]
      if greek_pattern.search(word1):
        record["words"] = [word2, word1]
      elif greek_pattern.search(word2):
        record["words"] = [word1, word2]
      elif english_pattern.search(word1):
        record["words"] = [word2, word1]
      elif english_pattern.search(word2):
        record["words"] = [word1, word2]

  def dump_list(self):
    self.auto_correction()
    with self.active_list_path.open("w", encoding="utf-8") as fout:
      fout.write(json.dumps(self.collection))

  def load_list(self):
    with self.active_list_path.open("r", encoding="utf-8") as fin:
      self.collection = json.loads(fin.read())
    self.auto_correction()


CONTEXT = Context()


def select_word():
  words = [
    idx for idx in range(len(CONTEXT.collection))
    if not CONTEXT.is_trained_word(idx) and not CONTEXT.is_word_active(idx)
  ][:SETTINGS.cards.active_pool_size]
  words += [
    idx for idx in range(len(CONTEXT.collection))
    if CONTEXT.is_trained_word(idx) and not CONTEXT.is_word_active(idx)
  ]
  weights = [
    1 if not CONTEXT.is_trained_word(idx) else
      0.5 * (0.95 ** (CONTEXT.collection[idx]["score"] / SETTINGS.cards.repetitions_to_train))
    for idx in words
  ]
  sum_of_trainded_weights = sum([0 if weight == 1 else weight for weight in weights]) / SETTINGS.cards.active_pool_size
  if sum_of_trainded_weights < 1:
    sum_of_trainded_weights = 1
  weights = [1 if weight == 1 else weight / sum_of_trainded_weights for weight in weights]
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
        if CONTEXT.score == SETTINGS.cards.train_length:
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
    self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Save).clicked.connect(self.add_word)
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.ui.word1.textChanged.connect(self.update_accept_button_state)
    self.ui.word2.textChanged.connect(self.update_accept_button_state)
    self.update_accept_button_state()

  def update_accept_button_state(self):
    word1_present = any(self.ui.word1.text() in x["words"] for x in CONTEXT.collection)
    word2_present = any(self.ui.word2.text() in x["words"] for x in CONTEXT.collection)
    acceptable = (
      self.ui.word1.text() != ""
      and self.ui.word2.text() != ""
      and not word1_present
      and not word2_present
    )
    self.ui.buttonBox.button(QDialogButtonBox.StandardButton.Save).setEnabled(acceptable)
    self.ui.status_label.setText("")
    if word1_present:
      self.ui.status_label.setText(f"Слово {self.ui.word1.text()} уже есть в коллекции")
    elif word2_present:
      self.ui.status_label.setText(f"Слово {self.ui.word2.text()} уже есть в коллекции")

  def add_word(self):
    word1 = self.ui.word1.text()
    word2 = self.ui.word2.text()
    CONTEXT.collection.append({"words": (word1, word2), "score": 0})
    CONTEXT.dump_list()
    self.main_window.setStatusTip(
      f"Слово/фраза {word1} теперь есть в списке {CONTEXT.active_list_name}."
    )
    update_menu_state(self.main_window)
    self.ui.word1.setText("")
    self.ui.word2.setText("")
    self.ui.status_label.setText("Слово добавлено")


class ChangeListDialog(QDialog):
  def __init__(self, main_window):
    super(ChangeListDialog, self).__init__()
    self.ui = ui_edit_words_list.Ui_Dialog()
    self.ui.setupUi(self)
    self.accepted.connect(self.save_list)
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.removed_words = []
    self.word_edits = []
    self.scores = []

    for index in range(len(CONTEXT.collection)):
      self.ui.words_list.addWidget(QLabel(str(index)), index, 0)
      self.word_edits.append([])
      for i in range(2):
        word_edit = QLineEdit()
        self.word_edits[-1].append(word_edit)
        self.ui.words_list.addWidget(word_edit, index, i + 1)
      self.scores.append(QLabel())
      self.ui.words_list.addWidget(self.scores[-1], index, 3)
      remove_button = QPushButton("Удалить")
      def gen_remove_callback(dialog, idx):
        def remove_item():
          updated_idx = idx
          for i in sorted(dialog.removed_words):
            if updated_idx >= i:
              updated_idx += 1
          dialog.removed_words.append(updated_idx)
          dialog.rerender()
        return remove_item
      remove_button.clicked.connect(gen_remove_callback(self, index))
      self.ui.words_list.addWidget(remove_button, index, 4)

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
    for i in reversed(range(len(CONTEXT.collection) - len(self.removed_words), self.ui.words_list.rowCount())):
      for j in reversed(range(self.ui.words_list.columnCount())):
        index = self.ui.words_list.indexOf(self.ui.words_list.itemAtPosition(i, j))
        if item := self.ui.words_list.takeAt(index):
          widget = item.widget()
          self.ui.words_list.removeWidget(widget)
          widget.deleteLater()
          del item
    row = 0
    for index, word in enumerate(CONTEXT.collection):
      if index in self.removed_words:
        continue
      for i in range(2):
        self.word_edits[row][i].setText(word["words"][i])
      self.scores[row].setText(str(word["score"]) + "/" + str(word.get("spelling_score", 0)))
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
    remote_sync_file(CONTEXT.active_list_path.relative_to(os.getcwd()))
    reset_stats()
    render_buttons()


class SpellingTrainDialog(QDialog):
  def __init__(self, main_window):
    super(SpellingTrainDialog, self).__init__()
    self.ui = ui_spelling_task.Ui_Dialog()
    self.ui.setupUi(self)
    self.main_window = main_window
    self.main_window.setStatusTip("")
    self.ui.check_answer_button.clicked.connect(self.check_answer)
    self.ui.continue_button.clicked.connect(self.next_word)
    self.check_if_input_is_empty()
    self.ui.answer_field.textChanged.connect(self.check_if_input_is_empty)
    self.ui.continue_button.setEnabled(False)
    self.ui.answer_field.setEnabled(False)
    words = [
      idx for idx in range(len(CONTEXT.collection))
      if not CONTEXT.is_spelling_trained_word(idx)
    ][:SETTINGS.spelling.active_pool_size]
    words += [
      idx for idx in range(len(CONTEXT.collection))
      if CONTEXT.is_spelling_trained_word(idx)
    ]
    weights = [
      1 if not CONTEXT.is_spelling_trained_word(idx) else
        0.5 * (0.95 ** (CONTEXT.collection[idx].get("spelling_score") / SETTINGS.spelling.repetitions_to_train))
      for idx in words
    ]
    sum_of_trainded_weights = sum([0 if weight == 1 else weight for weight in weights]) / SETTINGS.spelling.active_pool_size
    if sum_of_trainded_weights < 1:
      sum_of_trainded_weights = 1
    weights = [1 if weight == 1 else weight / sum_of_trainded_weights for weight in weights]
    self.words_to_check = random.choices(words, weights, k=SETTINGS.spelling.train_length)
    self.remove_current_word = False
    if greek_pattern.search(CONTEXT.collection[self.words_to_check[0]]["words"][0]):
      self.ref_idx = 1
      self.ans_idx = 0
    elif greek_pattern.search(CONTEXT.collection[self.words_to_check[1]]["words"][1]):
      self.ref_idx = 0
      self.ans_idx = 1
    elif english_pattern.search(CONTEXT.collection[self.words_to_check[0]]["words"][0]):
      self.ref_idx = 1
      self.ans_idx = 0
    else:
      self.ref_idx = 0
      self.ans_idx = 1
    self.next_word()

  def check_if_input_is_empty(self):
    self.ui.check_answer_button.setEnabled(self.ui.answer_field.text() != "")

  def check_answer(self):
    self.ui.answer.setText(CONTEXT.collection[self.words_to_check[0]]["words"][self.ans_idx])
    def normalize_word(word):
      normalized_str = unicodedata.normalize('NFD', word.strip().lower())
      filtered_str = ''.join(char for char in normalized_str if not unicodedata.combining(char))
      return filtered_str

    user_answer = normalize_word(self.ui.answer_field.text())
    correct_answer = normalize_word(CONTEXT.collection[self.words_to_check[0]]["words"][self.ans_idx])
    is_correct = user_answer == correct_answer
    self.remove_current_word = is_correct
    item_to_modify = CONTEXT.collection[self.words_to_check[0]]
    self.ui.answer.setStyleSheet("color: green" if is_correct else "color: red")
    if is_correct:
      item_to_modify["spelling_score"] = item_to_modify.get("spelling_score", 0) + 1
    else:
      item_to_modify["spelling_score"] = item_to_modify.get("spelling_score", 0) - 1
    if len(self.words_to_check) == 1 and self.remove_current_word:
      self.ui.continue_button.clicked.disconnect()
      self.ui.continue_button.clicked.connect(self.finish_train)
      self.ui.continue_button.setText("Завершить")
    self.ui.continue_button.setEnabled(True)
    self.ui.check_answer_button.setEnabled(False)
    self.ui.answer_field.setEnabled(False)

  def next_word(self):
    if self.remove_current_word:
      self.words_to_check = self.words_to_check[1:]
    else:
      self.words_to_check = self.words_to_check[1:] + [self.words_to_check[0]]
    self.ui.word_to_translate.setText(CONTEXT.collection[self.words_to_check[0]]["words"][self.ref_idx])
    self.ui.answer_field.setText("")
    self.ui.answer.setText("")
    self.ui.answer_field.setEnabled(True)
    self.ui.continue_button.setEnabled(False)

  def finish_train(self):
    CONTEXT.dump_list()
    remote_sync_file(CONTEXT.active_list_path.relative_to(os.getcwd()))
    self.close()


def can_modify_list():
  return CONTEXT.has_list


def can_start_train():
  return (CONTEXT.has_list and len(CONTEXT.collection) >= CARDS_COUNT)


def update_menu_state(main_window):
  main_window.ui.add_word.setVisible(can_modify_list())
  main_window.ui.start_train.setVisible(can_start_train())
  main_window.ui.change_list.setVisible(can_modify_list())
  main_window.ui.spelling_train.setVisible(can_start_train())


def reset_stats():
  CONTEXT.reset()


def start_train():
  reset_stats()
  fill_cards()
  CONTEXT.train_start = datetime.datetime.now()


class SettingsDialog(QDialog):
  def __init__(self):
    super(SettingsDialog, self).__init__()
    self.ui = ui_settings.Ui_Dialog()
    self.ui.setupUi(self)
    layout = QVBoxLayout()
    for excersize, params in dataclasses.asdict(SETTINGS).items():
      layout.addWidget(QLabel(LOCALIZATION[excersize]))
      form = QFormLayout()
      for parameter, value in params.items():
        spin_box = QSpinBox()
        spin_box.setValue(value)
        def generate_value_update(excers, param_name):
          return lambda i : setattr(excers, param_name, i)
        spin_box.valueChanged.connect(generate_value_update(getattr(SETTINGS, excersize), parameter))
        form.addRow(LOCALIZATION[parameter], spin_box)
      form_widget = QWidget()
      form_widget.setLayout(form)
      layout.addWidget(form_widget)
    self.setLayout(layout)
    self.finished.connect(save_settings)

class NetSettingsDialog(QDialog):
  def __init__(self):
    super(NetSettingsDialog, self).__init__()
    self.ui = ui_net_settings.Ui_NetSettings()
    self.ui.setupUi(self)
    self.ui.ip.setText(NET_SETTINGS.ip)
    self.ui.username.setText(NET_SETTINGS.user)
    self.ui.ip.textChanged.connect(lambda x: setattr(NET_SETTINGS, 'ip', x))
    self.ui.username.textChanged.connect(lambda x: setattr(NET_SETTINGS, 'user', x))
    self.accepted.connect(save_net_settings)


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
    self.ui.spelling_train.triggered.connect(lambda : SpellingTrainDialog(self).exec())
    self.ui.settings.triggered.connect(lambda : SettingsDialog().exec())
    self.ui.network_settings.triggered.connect(lambda : NetSettingsDialog().exec())
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
      local_sync_file(CONTEXT.active_list_path.relative_to(os.getcwd()))


if __name__ == "__main__":
  app = QApplication(sys.argv)

  window = App()
  window.show()

  app.exec()
  executor.shutdown(wait=True)
