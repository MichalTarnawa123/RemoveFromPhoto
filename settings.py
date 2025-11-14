import sys
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QGroupBox, QFormLayout, QScrollArea, QLineEdit

def open_settings(self):
    dialog = QDialog(self)
    dialog.setWindowTitle("Ustawienia SD + ControlNet")
    dialog.resize(680, 750)

    # --- CIEMNY MOTYW ---
    dialog.setStyleSheet("""
        QDialog {
            background-color: #1e1e1e;
            color: white;
        }
        QGroupBox {
            font-weight: bold;
            border: 1px solid #444;
            border-radius: 6px;
            margin: 10px;
            padding-top: 10px;
            background-color: #2d2d2d;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            subcontrol-position: top left;
            padding: 0 8px;
            color: #FFD700;
        }
        QLineEdit, QComboBox {
            background-color: #333;
            color: white;
            border: 1px solid #555;
            padding: 4px;
            border-radius: 4px;
        }
        QCheckBox, QRadioButton {
            color: white;
        }
        QLabel {
            color: white;
        }
        QSlider::groove:horizontal {
            border: 1px solid #444;
            height: 8px;
            background: #333;
            margin: 2px 0;
            border-radius: 4px;
        }
        QSlider::handle:horizontal {
            background: #FFD700;
            border: 1px solid #AAA;
            width: 16px;
            margin: -4px 0;
            border-radius: 8px;
        }
    """)

    layout = QVBoxLayout()
    scroll = QScrollArea()
    widget = QGroupBox()
    form = QFormLayout()

    self.prompt_edit = QLineEdit(self.saved_prompt)
    form.addRow("Prompt:", self.prompt_edit)
    self.neg_edit = QLineEdit(self.saved_negative_prompt)
    form.addRow("Negative Prompt:", self.neg_edit)

    # ==============================
    # Parametry Stable Diffusion
    # ==============================
    sd_group = QGroupBox("Parametry Stable Diffusion")
    sd_layout = QVBoxLayout()

    # --- Kroki ---






def save_settings(self, dialog):