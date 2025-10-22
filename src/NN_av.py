import onnxruntime as ort
import numpy as np
import json
import os

class TcNeuralPredictor:
    def __init__(self, model_path, params_path):
        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 1  
        sess_options.inter_op_num_threads = 1
        sess_options.log_severity_level = 3
        self.session = ort.InferenceSession(model_path, sess_options)
        self.input_name = self.session.get_inputs()[0].name
        with open(params_path, "r") as f:
            params = json.load(f)
        self.mean_input = np.array(params["mean_input"])
        self.std_input = np.array(params["std_input"])
        self.mean_output = params["mean_output"]
        self.std_output = params["std_output"]

    def predict(self, features):
        x_std = (np.array(features) - self.mean_input) / self.std_input
        x_std = x_std.astype(np.float32).reshape(1, -1)
        inputs = {
            self.input_name: x_std,
            "TrainingMode": np.array([False], dtype=bool)
        }
        pred_std = self.session.run(None, inputs)[0][0][0]
        return pred_std * self.std_output + self.mean_output


class EnsembleTcPredictor:
    def __init__(self, model_param_paths):
        self.predictors = [TcNeuralPredictor(m, p) for m, p in model_param_paths]

    def predict(self, features):
        preds = [predictor.predict(features) for predictor in self.predictors]
        return np.mean(preds)

# Initialize separate ensembles for QE and VASP
base_dir = os.path.dirname(os.path.abspath(__file__))

ensembles = {
    "QE": EnsembleTcPredictor([
        (os.path.join(base_dir, "model_QE_seed1.onnx"), os.path.join(base_dir, "params_QE_seed1.json")),
        (os.path.join(base_dir, "model_QE_seed2.onnx"), os.path.join(base_dir, "params_QE_seed2.json")),
        (os.path.join(base_dir, "model_QE_seed3.onnx"), os.path.join(base_dir, "params_QE_seed3.json")),
    ]),
    "VASP": EnsembleTcPredictor([
        (os.path.join(base_dir, "model_VASP_seed1.onnx"), os.path.join(base_dir, "params_VASP_seed1.json")),
        (os.path.join(base_dir, "model_VASP_seed2.onnx"), os.path.join(base_dir, "params_VASP_seed2.json")),
        (os.path.join(base_dir, "model_VASP_seed3.onnx"), os.path.join(base_dir, "params_VASP_seed3.json")),
    ])
}

def predict(features, code="QE"):
    code = code.upper()
    if code not in ensembles:
        raise ValueError(f"Unsupported code '{code}'. Valid codes are: {list(ensembles.keys())}")
    return ensembles[code].predict(features)

# Manual test
if __name__ == "__main__":
    example_input = [0.43, 0.54, 0.75, 0.1]
    print("QE model:")
    print(f"Tc = {predict(example_input, code='QE'):.2f} K")
    print("VASP model:")
    print(f"Tc = {predict(example_input, code='VASP'):.2f} K")
