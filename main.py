import sys
import os
from PyQt6.QtWidgets import QApplication
from config import Config
from ui.pet_widget import PetWidget
from ui.panel_widget import PanelWidget
from ui.setup_dialog import SetupDialog


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    config = Config()

    # 首次启动检测
    if not config.get("zhipu_api_key"):
        dlg = SetupDialog()
        if dlg.exec():
            config.set("zhipu_api_key", dlg.zhipu_key_input.text().strip())
            config.set("replicate_api_key", dlg.replicate_key_input.text().strip())
        else:
            sys.exit(0)

    pet = PetWidget(config)
    panel = PanelWidget(config)
    panel.set_pet_widget(pet)
    pet.set_panel(panel)

    pet.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
