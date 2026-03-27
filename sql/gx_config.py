import great_expectations as gx
import sys
print(sys.executable)

# ─────────────────────────────────────────────────────
# CONFIGURACION DEL ENTORNO
# ─────────────────────────────────────────────────────

NAME_DATA_SOURCE      = "sql_server"
NAME_DATA_ASSET       = "adidas"
NAME_BATCH_DEF        = "sql_tutorial"
NAME_EXPECTATION_SUITE = "sql_tutorial"
NAME_VALIDATION_DEF   = "sql_validation"
NAME_CHECKPOINT       = "sql_checkpoint"

# ─────────────────────────────────────────────────────
# DATOS DE LA CONEXION
# ─────────────────────────────────────────────────────

SQL_SERVER   = r"LAPTOP-27U46USM\SQLEXPRESS"          
SQL_DATABASE = "ADIDAS"          
SQL_SCHEMA   = "dbo"              
SQL_TABLE    = "VENTAS"          


CONNECTION_STRING = (
    f"mssql+pyodbc://{SQL_SERVER}/{SQL_DATABASE}"
    f"?driver=ODBC+Driver+17+for+SQL+Server"
    f"&trusted_connection=yes"          # autenticación Windows
)


# ─────────────────────────────────────────────────────
# STRING CON PASSWORD
# ─────────────────────────────────────────────────────
# CONNECTION_STRING = (
#     f"mssql+pyodbc://usuario:contraseña@{SQL_SERVER}/{SQL_DATABASE}"
#     f"?driver=ODBC+Driver+17+for+SQL+Server"
# )


# ─────────────────────────────────────────────────────
# PASO 1: INICIALIZAR CONTEXTO Y CONECTAR SQL SERVER
# ─────────────────────────────────────────────────────

context = gx.get_context(mode="file")


data_source = context.data_sources.add_or_update_sql(
    name=NAME_DATA_SOURCE,
    connection_string=CONNECTION_STRING,
)


data_asset = data_source.add_table_asset(
    name=NAME_DATA_ASSET,
    table_name=SQL_TABLE,
    schema_name=SQL_SCHEMA,
)


batch_definition = data_asset.add_batch_definition_whole_table(NAME_BATCH_DEF)

print("Paso 1: Conexión a SQL Server establecida")
print(f"Servidor : {SQL_SERVER}")
print(f"Base     : {SQL_DATABASE}")
print(f"Tabla    : {SQL_SCHEMA}.{SQL_TABLE}")


# ─────────────────────────────────────────────────────
# PASO 2: EXPECTATION SUITE
# ─────────────────────────────────────────────────────

try:
    context.suites.delete(NAME_EXPECTATION_SUITE)
except:
    pass

expectation_suite = gx.ExpectationSuite(name=NAME_EXPECTATION_SUITE)
expectation_suite = context.suites.add(expectation_suite)

# -- 2.1. COLUMNAS ESPERADAS
expected_columns = [
     "IdVendedor",
      "FechaVenta",
      "IdRegion",
      "IdEstado",
      "IdCiudad",
      "Producto",
      "IdFamilia",
      "IdGenero",
      "IdCategoria",
      "IdTipoProducto",
      "IdColor",
      "PrecioUnitario",
      "UnidadesVendidas",
      "PorcentajeRentabilidad",
      "IdTipoVenta",
]
expectation_suite.add_expectation(
    gx.expectations.ExpectTableColumnsToMatchSet(column_set=expected_columns)
)

# -- 2.2. VendorID SOLO PUEDE SER
expectation_suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="VendorID",
        value_set=[1185732 ],

)
)

# -- 2.3. VALIDACION DE NULOS
for column in ["IdVendedor","FechaVenta","IdRegion","IdEstado","IdCiudad","Producto","IdFamilia","IdGenero","IdCategoria","IdTipoProducto","IdColor","PrecioUnitario","UnidadesVendidas","PorcentajeRentabilidad","IdTipoVenta"]: 
        expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToNotBeNull(column=column)
    )

# -- 2.4. VALIDACIÓN DE RANGO
for column in ["IdCiudad"]:
    expectation_suite.add_expectation(
        gx.expectations.ExpectColumnValuesToBeBetween(
            column=column,
            min_value=1,
            max_value=52
        )
    )

# -- 2.5. IdColor entre 1 y 6
expectation_suite.add_expectation(
    gx.expectations.ExpectColumnValuesToBeInSet(
        column="IdColor",
        value_set=[1, 2, 3, 4, 5, 6],
    )
)

expectation_suite.add_expectation(
    gx.expectations.ExpectColumnMaxToBeBetween(
        column="IdColor",
        max_value=3,
    )
)


print("Paso 2: Expectation Suite configurada")


# ─────────────────────────────────────────────────────
# PASO 3: VALIDATION DEFINITION + CHECKPOINT
# ─────────────────────────────────────────────────────

validation_definition = gx.ValidationDefinition(
    data=batch_definition,
    suite=expectation_suite,
    name=NAME_VALIDATION_DEF,
)
context.validation_definitions.add_or_update(validation_definition)

checkpoint = gx.Checkpoint(
    name=NAME_CHECKPOINT,
    validation_definitions=[validation_definition],
    actions=[
        gx.checkpoint.UpdateDataDocsAction(name="update_all_data_docs"),
    ],
    result_format={"result_format": "COMPLETE"},
)
context.checkpoints.add_or_update(checkpoint)

print("Paso 3: Checkpoint guardado")


# ─────────────────────────────────────────────────────
# PASO 4: PRIMERA EJECUCIÓN
# ─────────────────────────────────────────────────────

runid = gx.RunIdentifier(run_name=f"Config run - {SQL_SCHEMA}.{SQL_TABLE}")
results = checkpoint.run(run_id=runid)