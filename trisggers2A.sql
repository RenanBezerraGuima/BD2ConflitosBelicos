-- TOTAL + EXCLUSIVA
-- Todo conflito pertence a um subtipo
-- Pertence a somente um subtipo

-- Trigger function
CREATE OR REPLACE FUNCTION check_total_exclusiva()
RETURNS TRIGGER AS $$
DECLARE
    count_tipos INT := 0;
BEGIN
    SELECT COUNT(*) INTO count_tipos FROM (
        SELECT CodConflito FROM Territorial WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Religioso WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Economico WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Racial WHERE CodConflito = NEW.CodConflito
    ) AS union_all;

    IF count_tipos != 1 THEN
        RAISE EXCEPTION 'Conflito % deve pertencer a exatamente um subtipo', NEW.CodConflito;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger
CREATE TRIGGER trg_total_exclusiva
AFTER INSERT OR UPDATE ON Conflito
FOR EACH ROW EXECUTE FUNCTION check_total_exclusiva();

-- PARA SELECIONAR O TRIGGER
ALTER TABLE Conflito ENABLE TRIGGER trg_total_exclusiva;