import great_expectations as gx

# ─────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────

NAME_CHECKPOINT = "sql_checkpoint"
SQL_TABLE       = "VENTAS"        # solo para el nombre del run

# ─────────────────────────────────────────────────────
# EJECUTAR CHECKPOINT
# ─────────────────────────────────────────────────────

context = gx.get_context(mode="file")

checkpoint = context.checkpoints.get(NAME_CHECKPOINT)
runid = gx.RunIdentifier(run_name=f"Validation run - {SQL_TABLE}")

# Sin batch_parameters: GX lee directo de la tabla configurada
results = checkpoint.run(run_id=runid)


print(f"Resultado: {'PASSED' if results.success else 'FAILED'}")
print("Reporte actualizado en: gx/uncommitted/data_docs/local_site/index.html")