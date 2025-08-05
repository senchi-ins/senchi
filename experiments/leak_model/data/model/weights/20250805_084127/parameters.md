INPUT_CHUNK  = 7 * 96 # 1 week history
OUTPUT_CHUNK = 24 # 6h forecast horizon
N_EPOCHS = 20
BATCH_SIZE = 32
NUM_LAYERS = 3
NUM_FILTERS = 64
KERNEL_SIZE = 3
DILATION = 2
DROPOUT = 0.1

total_houses=900
train_houses=720
test_houses=180

model = TCNModel(
    input_chunk_length = INPUT_CHUNK,
    output_chunk_length = OUTPUT_CHUNK,
    output_chunk_shift = 0,
    likelihood = BernoulliLikelihood(), 
    n_epochs = N_EPOCHS,
    batch_size = BATCH_SIZE,
    num_layers = NUM_LAYERS,
    num_filters = NUM_FILTERS,
    kernel_size = KERNEL_SIZE,
    dilation_base = DILATION,
    dropout = DROPOUT,
    random_state = 42,
)

t0 = time.time()
model.fit(series=train_targs,
        past_covariates=train_feats,
        val_series=val_targs,
        val_past_covariates=val_feats,
        max_samples_per_ts=5,
        verbose=True)
fit_secs = time.time() - t0
