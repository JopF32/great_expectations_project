import great_expectations as gx
import pandas as pd

# ─────────────────────────────────────────────────────
# CONFIGURACION DEL ENTORNO
# ─────────────────────────────────────────────────────

NAME_DATA_SOURCE = "pandas"
NAME_DATA_ASSET = "tutorial_data"
NAME_BATCH_DEF = "pandas_tutorial"
NAME_EXPECTATION_SUITE = "pandas_tutorial"
NAME_VALIDATION_DEF = "pandas_validation"
NAME_CHECKPOINT = "pandas"

FILE_CONFIGURE = "C:/Users/Jop_d/OneDrive/Documentos/PROYECTOS/great_expectations/data/data.csv"

df_configure = pd.read_csv(FILE_CONFIGURE)

# ─────────────────────────────────────────────────────
# PASO 1: INICIALIZAR CONTEXTO
# ─────────────────────────────────────────────────────

context = gx.get_context(mode="file")

data_source = context.data_sources.add_pandas(name=NAME_DATA_SOURCE)
data_asset = data_source.add_dataframe_asset(name=NAME_DATA_ASSET)
batch_definition = data_asset.add_batch_definition_whole_dataframe(NAME_BATCH_DEF)

# -- 2. CONFIGURACION DE LA SUITS DE EXPECTATIONS

expectation_suite = gx.ExpectationSuite(name=NAME_EXPECTATION_SUITE)
expectation_suite = context.suites.add(expectation_suite)

columns = list(df_configure.columns)
expectation = gx.expectations.ExpectTableColumnsToMatchSet(column_set=columns)
expectation_suite.add_expectation(expectation)

# -- 2.2. DEFINICION DE EXPECTATIVAS
# -- 2.2.1.  VENDOR ID ENTRE VALORES
expected_values = [1, 2]
expectation = gx.expectations.ExpectColumnValuesToBeInSet(
    column="VendorID",
    value_set=expected_values,
)
expectation_suite.add_expectation(expectation)

# -- 2.2.2. VALIDACIÓN DE NO NULOS
for column in columns:
    expectation = gx.expectations.ExpectColumnValuesToNotBeNull(column=column)
    expectation_suite.add_expectation(expectation)

# -- 2.2.3. VALIDACIÓN DE FORMATO
date_columns = ["tpep_pickup_datetime", "tpep_dropoff_datetime"]
DATE_PATTERN = (
    r"^(?:19|20)/d{2}-(0[1-9]|1[0-2])-(0[1-9]|[12]/d|3[01]) "
    r"(?:[01]/d|2[0-3]):[0-5]/d:[0-5]/d$"
)
for date_column in date_columns:
    expectation = gx.expectations.ExpectColumnValuesToMatchRegex(
        column=date_column,
        regex=DATE_PATTERN,
    )
    expectation_suite.add_expectation(expectation)

# -- 2.2.4. VALIDATE NON-ZERO COLUMNS
numeric_columns = [
    "passenger_count",
    "trip_distance",
    "tip_amount",
]
for numeric_column in numeric_columns:
    expectation = gx.expectations.ExpectColumnValuesToBeBetween(
        column=numeric_column,
        min_value=0,
    )
    expectation_suite.add_expectation(expectation)

# -- 2.3. EVALUATE RESULTS ON TEST DATASET
batch_parameters = {"dataframe": df_configure}
batch = batch_definition.get_batch(batch_parameters=batch_parameters)
validation_results = batch.validate(expectation_suite)

# -- 3. BUNDLE SUITE AND BATCH INTO VALIDATION DEFINITION AND CHECKPOINT W/ BUNDLED
# --    ACTIONS FOR EASY EXECUTION LATER
validation_definition = gx.ValidationDefinition(
    data=batch_definition,
    suite=expectation_suite,
    name=NAME_VALIDATION_DEF,
)
_ = context.validation_definitions.add(validation_definition)

action_list = [
    gx.checkpoint.UpdateDataDocsAction(
        name="update_all_data_docs",
    ),
]
checkpoint = gx.Checkpoint(
    name=NAME_CHECKPOINT,
    validation_definitions=[validation_definition],
    actions=action_list,
    result_format={
        "result_format": "COMPLETE",
    },
)
_ = context.checkpoints.add(checkpoint)

file_identifier = FILE_CONFIGURE.split("/")[-1]
runid = gx.RunIdentifier(run_name=f"Configuration run - {file_identifier}")
results = checkpoint.run(batch_parameters=batch_parameters, run_id=runid)