from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QVBoxLayout, QWidget, QLabel, QStatusBar, QPushButton, QHBoxLayout, QComboBox, QWidgetAction
from PySide6.QtGui import QAction
from vtkmodules.vtkRenderingCore import vtkRenderer
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera, vtkInteractorStyleJoystickCamera, vtkInteractorStyleRubberBandZoom
import sys
from pathlib import Path
import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(".fdd Visualisierer")
        self.setGeometry(100, 100, 1024, 768)

        # Menüleiste
        menu_bar = self.menuBar()

        # File Menü
        file_menu = menu_bar.addMenu("File")

        load_action = QAction("Load", self)
        load_action.triggered.connect(self.load_model)
        file_menu.addAction(load_action)

        save_action = QAction("Save", self)
        save_action.triggered.connect(self.save_model)
        file_menu.addAction(save_action)

        import_fdd_action = QAction("Import FDD", self)
        import_fdd_action.triggered.connect(self.import_fdd)
        file_menu.addAction(import_fdd_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View Menü
        view_menu = menu_bar.addMenu("View")

        # Interactor Style Menü
        self.interactor_style_dropdown = QComboBox(self)
        self.interactor_style_dropdown.addItem("Trackball Camera", vtkInteractorStyleTrackballCamera)
        self.interactor_style_dropdown.addItem("Joystick Camera", vtkInteractorStyleJoystickCamera)
        self.interactor_style_dropdown.addItem("Rubber Band Zoom", vtkInteractorStyleRubberBandZoom)
        self.interactor_style_dropdown.currentIndexChanged.connect(self.change_interactor_style)

        # dropdown in View Menü hinzufügen
        dropdown_action = QWidgetAction(self)
        dropdown_action.setDefaultWidget(self.interactor_style_dropdown)
        view_menu.addAction(dropdown_action)

        # Ansicht zurücksetzen Knopf
        reset_view_action = QAction("Ansicht zurücksetzen", self)
        reset_view_action.triggered.connect(self.reset_view)
        view_menu.addAction(reset_view_action)

        # Statusleiste
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar_label = QLabel("No file loaded.")
        self.status_bar.addWidget(self.status_bar_label)

        # VTK Render Widget
        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        layout = QVBoxLayout()
        self.central_widget.setLayout(layout)

        self.vtk_widget = QVTKRenderWindowInteractor(self.central_widget)
        layout.addWidget(self.vtk_widget)
        self.renderer = vtkRenderer()
        self.vtk_widget.GetRenderWindow().AddRenderer(self.renderer)

        # Add coordinate system
        self.add_coordinate_system()

        # Layout knöpfe
        button_layout = QHBoxLayout()
        layout.addLayout(button_layout)

        # Knopf Hintergrundfarbe
        self.toggle_bg_button = QPushButton("Hintergrundfarbe Schwarz/weiß", self)
        self.toggle_bg_button.clicked.connect(self.toggle_background)
        button_layout.addWidget(self.toggle_bg_button)

        # Knopf Kräfte ausblenden
        self.toggle_bodies_button = QPushButton("Kräfte ausblenden", self)
        self.toggle_bodies_button.clicked.connect(self.toggle_bodies_only)
        button_layout.addWidget(self.toggle_bodies_button)

        self.is_black_background = True  # Initialisierung Hintergrundfarbe
        self.show_bodies_only = False  # initialisierung Kräfte ausblenden

        self.current_model = None

    def add_coordinate_system(self):
        axes = vtkAxesActor()
        self.orientation_marker = vtkOrientationMarkerWidget()
        self.orientation_marker.SetOrientationMarker(axes)
        self.orientation_marker.SetInteractor(self.vtk_widget.GetRenderWindow().GetInteractor())
        self.orientation_marker.SetViewport(0.8, 0.0, 1.0, 0.2)  # Rechte untere ecke
        self.orientation_marker.SetEnabled(1)
        self.orientation_marker.InteractiveOff()

        self.vtk_widget.GetRenderWindow().Render()

    def load_model(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open Model File", "", "JSON Files (*.json)")
        if file_path:
            self.clear_renderer()
            self.current_model = mbsModel.mbsModel()
            self.current_model.loadDatabase(file_path)
            self.current_model.showModel(self.renderer)
            self.status_bar_label.setText(f"Loaded: {file_path}")
            self.vtk_widget.GetRenderWindow().Render()

    def save_model(self):
        if self.current_model is None:
            self.status_bar_label.setText("No model loaded to save!")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save Model File", "", "JSON Files (*.json)")
        if file_path:
            json_path = Path(file_path).with_suffix(".json")
            self.current_model.saveDatabase(json_path)
            self.status_bar_label.setText(f"Saved to: {json_path}")

    def import_fdd(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Open FDD File", "", "FDD Files (*.fdd)")
        if file_path:
            self.clear_renderer()
            self.status_bar_label.setText(f"Loaded: {file_path}")
            self.visualize_model(Path(file_path))

    def visualize_model(self, fdd_path):
        myModel = mbsModel.mbsModel()
        myModel.importFddFile(fdd_path)
        json_path = fdd_path.with_suffix(".json")
        myModel.saveDatabase(json_path)

        self.current_model = mbsModel.mbsModel()
        self.current_model.loadDatabase(json_path)
        self.current_model.showModel(self.renderer)

        self.vtk_widget.GetRenderWindow().Render()

    def clear_renderer(self):
        self.renderer.RemoveAllViewProps()

    def toggle_background(self):
        if self.is_black_background:
            self.renderer.SetBackground(1, 1, 1)  # Weißer Hintergrund
        else:
            self.renderer.SetBackground(0, 0, 0)  # Schwarzer Hintergrund
        self.is_black_background = not self.is_black_background
        self.vtk_widget.GetRenderWindow().Render()

    def toggle_bodies_only(self):
        if self.current_model:
            self.show_bodies_only = not self.show_bodies_only
            self.clear_renderer()
            if self.show_bodies_only:
                self.current_model.showBodiesOnly(self.renderer)
            else:
                self.current_model.showModel(self.renderer)
            self.vtk_widget.GetRenderWindow().Render()

    def change_interactor_style(self, index):
        style_class = self.interactor_style_dropdown.itemData(index)
        interactor = self.vtk_widget.GetRenderWindow().GetInteractor()
        interactor.SetInteractorStyle(style_class())
        self.vtk_widget.GetRenderWindow().Render()

    def reset_view(self):
        camera = self.renderer.GetActiveCamera()
        camera.SetPosition(0, 0, 1)
        camera.SetFocalPoint(0, 0, 0)
        camera.SetViewUp(0, 1, 0)
        self.renderer.ResetCamera()
        self.vtk_widget.GetRenderWindow().Render()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())