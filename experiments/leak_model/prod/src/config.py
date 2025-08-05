# Config for the model
from darts.utils.likelihood_models.torch import BernoulliLikelihood

HYPERPARAMS = {
    "INPUT_CHUNK"  : 7 * 96, # 1 week history
    "OUTPUT_CHUNK" : 24, # 24 h forecast horizon
    "OUTPUT_CHUNK_SHIFT" : 0,
    "LIKELIHOOD" : BernoulliLikelihood(),
    "N_EPOCHS" : 20,
    "BATCH_SIZE" : 32,
    "NUM_LAYERS" : 3,
    "NUM_FILTERS" : 64,
    "KERNEL_SIZE" : 3,
    "DILATION" : 2,
    "DROPOUT" : 0.1,
    "RANDOM_STATE" : 42,
}

NUMERICAL_FEATURES = [
    'velocity_m_per_s', 'flow_m3_s', 'flow_gpm', 'upstream_transit_time_s',
    'downstream_transit_time_s', 'delta_t_ns', 'pipe_width_in', 'od_mm',
    'wall_mm', 'id_mm', 'l_path_m', 'c_est_m_per_s', 'temp_est_c',
    'n_traverses', 'theta_deg'
]

FEATURES = [
    'velocity_m_per_s', 'flow_m3_s', 'upstream_transit_time_s',
    'downstream_transit_time_s', 'delta_t_ns', 'pipe_width_in', 'od_mm',
    'wall_mm', 'id_mm', 'l_path_m', 'c_est_m_per_s', 'temp_est_c',
    'n_traverses', 'theta_deg', 'pipe_material_onehot_Copper',
    'pipe_material_onehot_PEX', 'leak_type_onehot_burst_freeze',
    'leak_type_onehot_burst_pressure', 'leak_type_onehot_gradual',
    'leak_type_onehot_micro', 'leak_type_onehot_none',
    'leak_category_onehot_dish', 'leak_category_onehot_faucet',
    'leak_category_onehot_laundry', 'leak_category_onehot_none',
    'leak_category_onehot_shower', 'leak_category_onehot_toilet',
    'leak_category_onehot_unknown', 'leak_pipe_onehot_P_DISHWASHER',
    'leak_pipe_onehot_P_ENS_LAV', 'leak_pipe_onehot_P_ENS_SHWR',
    'leak_pipe_onehot_P_ENS_WC', 'leak_pipe_onehot_P_FAM_LAV',
    'leak_pipe_onehot_P_FAM_TUB', 'leak_pipe_onehot_P_FAM_WC',
    'leak_pipe_onehot_P_HOSE_BACK', 'leak_pipe_onehot_P_HOSE_FRONT',
    'leak_pipe_onehot_P_KITCHEN_BRANCH', 'leak_pipe_onehot_P_KITCHEN_SINK',
    'leak_pipe_onehot_P_LAUNDRY', 'leak_pipe_onehot_P_MAIN_1',
    'leak_pipe_onehot_P_MAIN_2', 'leak_pipe_onehot_P_POWDER_BRANCH',
    'leak_pipe_onehot_P_POWDER_LAV', 'leak_pipe_onehot_P_POWDER_WC',
    'leak_pipe_onehot_P_UPPER_BRANCH', 'leak_pipe_onehot_P_WATER_HEATER',
    'leak_pipe_onehot_none'
]

TARGETS = [
    'pipe_burst_leak_next_24h',
    'leak_branch_onehot_KITCHEN_BRANCH_next_24h',
    'leak_branch_onehot_MAIN_TRUNK_1_next_24h',
    'leak_branch_onehot_MAIN_TRUNK_2_next_24h',
    'leak_branch_onehot_POWDER_ROOM_BRANCH_next_24h',
    'leak_branch_onehot_UPPER_FLOOR_BRANCH_next_24h',
    'leak_branch_onehot_none_next_24h',
    'leak_branch_onehot_unknown_next_24h'
]

# TODO: Check if numberical features can be consolidated
NUMERICAL_FEATURES_v1 = [
    'velocity_m_per_s', 'flow_m3_s', 'upstream_transit_time_s', 
    'downstream_transit_time_s', 'delta_t_ns', 'pipe_width_in',
    'od_mm', 'wall_mm', 'id_mm', 'c_est_m_per_s', 'temp_est_c'
]

NUMERICAL_FEATURES_v2 = [
    'velocity_m_per_s', 'flow_m3_s', 'flow_gpm', 'upstream_transit_time_s',
    'downstream_transit_time_s', 'delta_t_ns', 'pipe_width_in', 'od_mm',
    'wall_mm', 'id_mm', 'l_path_m', 'c_est_m_per_s', 'temp_est_c',
    'n_traverses', 'theta_deg'
]

CATEGORICAL_FEATURES_v1 = [
    'pipe_material', 'leak_type', 'leak_category', 'leak_pipe'
]

TARGET_COLUMNS = ['pipe_burst_leak', 'leak_branch']

NAN_COLS = ['leak_category','leak_branch','leak_pipe'] 