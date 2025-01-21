from PySide6.QtWidgets import QMainWindow, QApplication, QFileDialog, QVBoxLayout, QWidget, QLabel, QStatusBar, QMenuBar 
from PySide6.QtGui import QAction
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkCamera
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingAnnotation import vtkAxesActor
from vtkmodules.vtkInteractionWidgets import vtkOrientationMarkerWidget  # Corrected import
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import vtkRenderWindowInteractor
import sys
from pathlib import Path
import mbsModel

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VTK with Qt File Integration")
        self.setGeometry(100, 100, 1024, 768)

        # Menüleiste
        menu_bar = self.menuBar()

        # File menu
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

        self.current_model = None

    def add_coordinate_system(self):
        axes = vtkAxesActor()
        self.orientation_marker = vtkOrientationMarkerWidget()
        self.orientation_marker.SetOrientationMarker(axes)
        self.orientation_marker.SetInteractor(self.vtk_widget.GetRenderWindow().GetInteractor())
        self.orientation_marker.SetViewport(0.8, 0.0, 1.0, 0.2)  # Bottom right corner
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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())