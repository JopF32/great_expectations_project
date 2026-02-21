import great_expectations as gx
import pandas as pd


NAME_CHECKPOINT = "pandas"
FILE_TEST = "C:/Users/Jop_d/OneDrive/Documentos/PROYECTOS/great_expectations/data/data.csv"


context = gx.get_context(mode="file")


df_validate = pd.read_csv(FILE_TEST)
batch_parameters = {"dataframe": df_validate}

checkpoint = context.checkpoints.get(NAME_CHECKPOINT)
file_identifier = FILE_TEST.split("/")[-1]
runid = gx.RunIdentifier(run_name=f"Test run - {file_identifier}")

results = checkpoint.run(batch_parameters=batch_parameters, run_id=runid)