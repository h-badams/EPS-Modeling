import numpy as np
# quantify error between prediction and test data

def net_mse(test_times, test_values, pred_times, pred_values):
    if abs(test_times[-1] - pred_times[-1]) > 30:
        raise Exception('Big difference between test length and prediction length')
    interpolated_pred_values = np.interp(x=test_times, xp=pred_times, fp=pred_values)
    mse = np.mean((interpolated_pred_values - test_values) ** 2)
    return mse