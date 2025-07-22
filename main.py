from ui.visualizer import OfficeLayoutVisualizer
from core.simulator import Simulator

if __name__ == "__main__":
    visualizer = OfficeLayoutVisualizer("config/config.json")
    simulator = Simulator(visualizer=visualizer, genetic=visualizer.genetic)
    simulator.run()
