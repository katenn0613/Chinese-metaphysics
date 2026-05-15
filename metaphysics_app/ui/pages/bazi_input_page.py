from __future__ import annotations

from PySide6.QtCore import QDateTime, QLocale, Signal
from PySide6.QtGui import QDoubleValidator
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDateTimeEdit,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from metaphysics_app.config import DEFAULT_TIMEZONE
from metaphysics_app.domain.models import BirthInfo, CalendarType, Gender
from metaphysics_app.ui.components import page_title, primary_button


class BaziInputPage(QWidget):
    generate_requested = Signal(object)

    def __init__(
        self, default_timezone: str = DEFAULT_TIMEZONE, default_true_solar_time: bool = True
    ) -> None:
        super().__init__()
        self.default_timezone = default_timezone
        self.default_true_solar_time = default_true_solar_time
        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 28)
        layout.setSpacing(16)
        layout.addWidget(page_title("八字排盘"))

        form = QFormLayout()
        self.calendar_combo = QComboBox()
        self.calendar_combo.addItem("阳历", CalendarType.SOLAR.value)
        self.calendar_combo.addItem("农历", CalendarType.LUNAR.value)
        form.addRow("历法", self.calendar_combo)

        self.datetime_edit = QDateTimeEdit(QDateTime.currentDateTime())
        self.datetime_edit.setCalendarPopup(True)
        self.datetime_edit.setDisplayFormat("yyyy-MM-dd HH:mm")
        form.addRow("出生时间", self.datetime_edit)

        self.birthplace_input = QLineEdit()
        self.birthplace_input.setPlaceholderText("例如：上海")
        form.addRow("出生地", self.birthplace_input)

        self.longitude_input = QLineEdit()
        self.longitude_input.setPlaceholderText("例如：121.47，可留空")
        longitude_validator = QDoubleValidator(-180.0, 180.0, 6, self)
        longitude_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        longitude_validator.setLocale(QLocale.c())
        self.longitude_input.setValidator(longitude_validator)
        form.addRow("经度", self.longitude_input)

        self.latitude_input = QLineEdit()
        self.latitude_input.setPlaceholderText("例如：31.23，可留空")
        latitude_validator = QDoubleValidator(-90.0, 90.0, 6, self)
        latitude_validator.setNotation(QDoubleValidator.Notation.StandardNotation)
        latitude_validator.setLocale(QLocale.c())
        self.latitude_input.setValidator(latitude_validator)
        form.addRow("纬度", self.latitude_input)

        self.timezone_input = QLineEdit(default_timezone)
        form.addRow("时区", self.timezone_input)

        self.gender_combo = QComboBox()
        self.gender_combo.addItem("未知", Gender.UNKNOWN.value)
        self.gender_combo.addItem("女", Gender.FEMALE.value)
        self.gender_combo.addItem("男", Gender.MALE.value)
        self.gender_combo.addItem("其他", Gender.OTHER.value)
        form.addRow("性别", self.gender_combo)

        self.true_solar_checkbox = QCheckBox("启用真太阳时修正")
        self.true_solar_checkbox.setChecked(default_true_solar_time)
        form.addRow("修正", self.true_solar_checkbox)
        layout.addLayout(form)

        actions = QHBoxLayout()
        generate = primary_button("生成排盘")
        clear = QPushButton("清空")
        generate.clicked.connect(self._emit_generate)
        clear.clicked.connect(self._clear)
        actions.addWidget(generate)
        actions.addWidget(clear)
        actions.addStretch()
        layout.addLayout(actions)
        layout.addStretch()

    def _emit_generate(self) -> None:
        try:
            birth_info = BirthInfo(
                birth_datetime=self.datetime_edit.dateTime().toPython(),
                calendar_type=CalendarType(self.calendar_combo.currentData()),
                birthplace_name=self.birthplace_input.text().strip(),
                timezone=self.timezone_input.text().strip() or DEFAULT_TIMEZONE,
                gender=Gender(self.gender_combo.currentData()),
                use_true_solar_time=self.true_solar_checkbox.isChecked(),
                longitude=self._optional_float(self.longitude_input.text()),
                latitude=self._optional_float(self.latitude_input.text()),
            )
        except ValueError as exc:
            QMessageBox.warning(self, "输入有误", str(exc))
            return
        self.generate_requested.emit(birth_info)

    def _optional_float(self, value: str) -> float | None:
        value = value.strip()
        if not value:
            return None
        return float(value)

    def _clear(self) -> None:
        self.datetime_edit.setDateTime(QDateTime.currentDateTime())
        self.calendar_combo.setCurrentIndex(0)
        self.birthplace_input.clear()
        self.longitude_input.clear()
        self.latitude_input.clear()
        self.timezone_input.setText(self.default_timezone)
        self.gender_combo.setCurrentIndex(0)
        self.true_solar_checkbox.setChecked(self.default_true_solar_time)

    def apply_defaults(self, default_timezone: str, default_true_solar_time: bool) -> None:
        self.default_timezone = default_timezone
        self.default_true_solar_time = default_true_solar_time
        if not self.timezone_input.text().strip() or self.timezone_input.text() == DEFAULT_TIMEZONE:
            self.timezone_input.setText(default_timezone)
        self.true_solar_checkbox.setChecked(default_true_solar_time)
