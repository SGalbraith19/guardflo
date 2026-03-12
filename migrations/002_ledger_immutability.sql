-- Prevent UPDATE on financial_ledger
CREATE OR REPLACE FUNCTION prevent_ledger_update()
RETURNS trigger AS $$
BEGIN
   RAISE EXCEPTION 'FinancialLedger is immutable: UPDATE not allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_ledger_update
BEFORE UPDATE ON financial_ledger
FOR EACH ROW
EXECUTE FUNCTION prevent_ledger_update();


-- Prevent DELETE on financial_ledger
CREATE OR REPLACE FUNCTION prevent_ledger_delete()
RETURNS trigger AS $$
BEGIN
   RAISE EXCEPTION 'FinancialLedger is immutable: DELETE not allowed';
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER no_ledger_delete
BEFORE DELETE ON financial_ledger
FOR EACH ROW
EXECUTE FUNCTION prevent_ledger_delete();