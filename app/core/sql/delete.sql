BEGIN;

-- Remove todas as tuplas de todas as tabelas
TRUNCATE TABLE GrupoArmado, LiderPolitico, Divisao, ChefeMilitar, Conflito, ConflitoPais, Territorial, Religioso, Economico, Racial, EntPart, OrganizacaoM, EntradMed, Dialoga, Traficante, TipoArma, PodeFornecer, Fornece CASCADE;

COMMIT;
